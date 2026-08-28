import mailbox
import uuid
import email
from pathlib import Path
from email.message import Message
from ingestion.application.ports.parser_port import DocumentParserPort
from ingestion.domain.entities import RawDocument
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError

class EnronEmailParserAdapter(DocumentParserPort):
    """Parses real Enron email corpus files (mbox or per-custodian folders) downloaded via
    scripts/load_enron_dataset.py.
    """

    def parse(self, source_path: str) -> list[RawDocument]:
        documents = []
        path = Path(source_path)
        
        if not path.exists():
            raise ExternalServiceError(f"Enron email path not found: {source_path}")
            
        try:
            if path.is_file():
                if path.suffix == '.mbox':
                    mb = mailbox.mbox(path)
                    for message in mb:
                        documents.append(self._parse_message(message, str(path)))
                elif path.suffix == '.txt' or path.suffix == '.eml':
                    with open(path, 'rb') as f:
                        msg = email.message_from_binary_file(f)
                        documents.append(self._parse_message(msg, str(path)))
                else:
                    raise ExternalServiceError(f"Unsupported file extension for Enron parser: {path.suffix}")
            elif path.is_dir():
                # Parse all .txt or .eml files in directory
                for filepath in path.rglob("*"):
                    if filepath.is_file() and (filepath.suffix in ['.txt', '.eml'] or not filepath.suffix):
                        with open(filepath, 'rb') as f:
                            msg = email.message_from_binary_file(f)
                            documents.append(self._parse_message(msg, str(filepath)))
        except Exception as e:
            raise ExternalServiceError(f"Failed to parse Enron emails {source_path}: {e}")
            
        return documents
        
    def _parse_message(self, message: Message, source_path: str) -> RawDocument:
        subject = message.get("Subject", "")
        from_ = message.get("From", "")
        to = message.get("To", "")
        date = message.get("Date", "")
        
        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(errors="replace") if isinstance(payload, bytes) else str(payload)
        else:
            payload = message.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="replace") if isinstance(payload, bytes) else str(payload)
            
        raw_text = f"From: {from_}\nTo: {to}\nDate: {date}\nSubject: {subject}\n\n{body}"
        
        return RawDocument(
            document_id=str(uuid.uuid4()),
            source_type=SourceType.ENRON_EMAILS,
            raw_text=raw_text,
            source_path=source_path
        )
