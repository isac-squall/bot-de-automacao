import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from modules.message_sender import MessageSender


class MessageSenderCsvTests(unittest.TestCase):
    def write_contacts(self, directory: str) -> Path:
        csv_path = Path(directory) / "contacts.csv"
        contacts = [
            {
                "nome": "Contato Exemplo 1",
                "telefone": "+55 (11) 99999-0001",
                "pedido": "PED-DEMO-001",
                "status": "Aprovado",
            },
            {
                "nome": "Contato Exemplo 2",
                "telefone": "21 3000-0002",
                "pedido": "PED-DEMO-002",
                "status": "Em Transporte",
            },
        ]

        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=contacts[0].keys())
            writer.writeheader()
            writer.writerows(contacts)

        return csv_path

    def test_previsualizar_envios_personaliza_e_normaliza_telefones(self):
        with TemporaryDirectory() as directory:
            csv_path = self.write_contacts(directory)
            sender = MessageSender(web_automator=Mock())

            preview = sender.previsualizar_envios(
                caminho_csv=csv_path,
                template="Oi {nome}, pedido {pedido}: {status}",
            )

        self.assertEqual(
            preview,
            [
                {
                    "nome": "Contato Exemplo 1",
                    "telefone": "5511999990001",
                    "mensagem": "Oi Contato Exemplo 1, pedido PED-DEMO-001: Aprovado",
                },
                {
                    "nome": "Contato Exemplo 2",
                    "telefone": "552130000002",
                    "mensagem": "Oi Contato Exemplo 2, pedido PED-DEMO-002: Em Transporte",
                },
            ],
        )

    def test_simulacao_processa_csv_e_notifica_progresso_sem_abrir_navegador(self):
        with TemporaryDirectory() as directory:
            csv_path = self.write_contacts(directory)
            web_automator = Mock()
            sender = MessageSender(web_automator=web_automator)
            progress: list[tuple[int, int, str]] = []

            def on_progress(current: int, total: int, message: str) -> None:
                progress.append((current, total, message))

            with patch("modules.message_sender.time.sleep") as sleep:
                result = sender.disparar_lote_whatsapp(
                    caminho_csv=csv_path,
                    template="Oi {nome}, pedido {pedido}: {status}",
                    modo_simulacao=True,
                    callback_progresso=on_progress,
                )

        self.assertEqual(result, {"total": 2, "sucessos": 2, "erros": 0})
        self.assertEqual(len(progress), 3)
        self.assertEqual(progress[0][:2], (1, 2))
        self.assertIn("Contato Exemplo 1", progress[0][2])
        self.assertEqual(progress[1][:2], (2, 2))
        self.assertEqual(progress[2][:2], (2, 2))
        self.assertIn("Sucessos: 2 | Falhas: 0", progress[2][2])
        self.assertEqual(sleep.call_count, 2)
        web_automator.iniciar_navegador.assert_not_called()


if __name__ == "__main__":
    unittest.main()
