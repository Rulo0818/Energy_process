import pytest
import xml.etree.ElementTree as ET
from app.services.parser import ParserService
from app.models.domain import Client, ProcessedFile
from sqlmodel import Session, SQLModel, create_engine
from datetime import datetime

# In-memory DB for testing
engine = create_engine("sqlite:///:memory:")

@pytest.fixture
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_parser_success(session):
    # Setup Data
    client = Client(cups="ES0021000000000000XX", name="Test Client")
    session.add(client)
    session.commit()

    # XML Mock
    xml_content = b"""
    <Root>
        <Cabecera><CUPS>ES0021000000000000XX</CUPS></Cabecera>
        <InstalacionGenAutoconsumo>12</InstalacionGenAutoconsumo>
        <Periodo>
            <FechaDesde>2023-01-01</FechaDesde>
            <FechaHasta>2023-01-31</FechaHasta>
            <ValorEnergiaNetaGen>100.5</ValorEnergiaNetaGen>
            <ValorEnergiaAutoconsumida>50.2</ValorEnergiaAutoconsumida>
        </Periodo>
    </Root>
    """
    
    parser = ParserService(session)
    record = parser.process_file(xml_content, "file1.xml")
    
    assert record.cups == "ES0021000000000000XX"
    assert record.tipo_autoconsumo == "12"
    assert record.valor_energia_neta_gen[0] == 100.5
    assert record.valor_energia_autoconsumida[0] == 50.2

def test_parser_client_not_found(session):
    xml_content = b"""
    <Root>
        <Cabecera><CUPS>ES0021000000000000XX</CUPS></Cabecera>
    </Root>
    """
    parser = ParserService(session)
    import fastapi
    with pytest.raises(fastapi.HTTPException) as excinfo:
        parser.process_file(xml_content, "file2.xml")
    assert "No existe el cliente" in str(excinfo.value.detail)

def test_parser_duplicate_file(session):
     # Setup Data
    session.add(ProcessedFile(filename="file_dup.xml"))
    session.commit()
    
    xml_content = b"<Root></Root>"
    parser = ParserService(session)
    import fastapi
    with pytest.raises(fastapi.HTTPException) as excinfo:
        parser.process_file(xml_content, "file_dup.xml")
    assert f"El archivo 'file_dup.xml' ya ha sido procesado" in str(excinfo.value.detail)
