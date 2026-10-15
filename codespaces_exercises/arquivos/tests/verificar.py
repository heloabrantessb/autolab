"""Execute com Python; as falhas do starter indicam TODOs ainda pendentes."""

import argparse
import csv
from io import StringIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apoio import organizar


class CriteriosOrganizacao(unittest.TestCase):
    def test_categorias(self):
        for nome, esperado in (
            ("a.pdf", "Documentos"), ("a.doc", "Documentos"), ("a.DOCX", "Documentos"),
            ("a.txt", "Documentos"), ("a.csv", "Planilhas"), ("a.xls", "Planilhas"),
            ("a.XLSX", "Planilhas"), ("a.png", "Imagens"), ("a.JPG", "Imagens"),
            ("a.jpeg", "Imagens"), ("LEIA-ME", "Outros"), ("a.zip", "Outros"),
        ):
            with self.subTest(nome=nome):
                self.assertEqual(solucao.categoria(nome), esperado)

    def test_colisoes_sem_distinguir_maiusculas(self):
        usados = set()
        self.assertEqual(solucao.nome_unico("relatorio.txt", usados), "relatorio.txt")
        self.assertEqual(solucao.nome_unico("RELATORIO.TXT", usados), "RELATORIO_2.TXT")
        self.assertIn("relatorio_2.txt", usados)
        self.assertEqual(solucao.nome_unico("relatorio.txt", usados), "relatorio_3.txt")

    def test_colisao_com_sufixo_existente_e_sem_extensao(self):
        usados = {"a.txt", "a_2.txt"}
        self.assertEqual(solucao.nome_unico("a.txt", usados), "a_3.txt")
        self.assertEqual(solucao.nome_unico("LEIA-ME", {"leia-me"}), "LEIA-ME_2")

    def test_inventario_preserva_caminhos_e_status(self):
        self.assertEqual(solucao.linha_inventario("sub/a.txt", "Documentos/a_2.txt", "Documentos"),
                         ("sub/a.txt", "Documentos/a_2.txt", "Documentos", "renomeado"))
        self.assertEqual(solucao.linha_inventario("a.txt", "Documentos/a.txt", "Documentos"),
                         ("a.txt", "Documentos/a.txt", "Documentos", "organizado"))

    def test_zip_exemplo_preserva_seis_arquivos_e_inventario(self):
        with TemporaryDirectory() as area:
            saida = Path(area) / "resultado.zip"
            contagens = organizar(solucao.categoria, solucao.nome_unico, solucao.linha_inventario, saida)
            self.assertEqual(contagens, {"Documentos": 3, "Planilhas": 1, "Imagens": 1, "Outros": 1})
            with ZipFile(saida) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(len(archive.namelist()), 11)
                self.assertNotEqual(archive.read("Documentos/comunicado.txt"), archive.read("Documentos/comunicado_2.txt"))
                rows = list(csv.DictReader(StringIO(archive.read("relatorio.csv").decode("utf-8"))))
                self.assertEqual(len(rows), 6)
                self.assertEqual(list(rows[0]), ["caminho_original", "nome_saida", "categoria", "status"])
                self.assertEqual(sum(row["status"] == "renomeado" for row in rows), 1)
                self.assertTrue(all(row["nome_saida"] in archive.namelist() for row in rows))

    def test_saida_existente_nao_e_sobrescrita(self):
        with TemporaryDirectory() as area:
            saida = Path(area) / "resultado.zip"
            saida.write_bytes(b"preservar")
            with self.assertRaises(FileExistsError):
                organizar(solucao.categoria, solucao.nome_unico, solucao.linha_inventario, saida)
            self.assertEqual(saida.read_bytes(), b"preservar")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verifica a solução local, sem enviar código ao site.")
    parser.add_argument("--referencia", action="store_true", help="Uso do instrutor no repositório completo.")
    args = parser.parse_args()
    if args.referencia:
        import referencia as solucao
    else:
        import starter as solucao
    unittest.main(argv=[sys.argv[0]], verbosity=2)
