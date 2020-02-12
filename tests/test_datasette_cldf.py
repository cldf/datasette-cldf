
def test_StructureDataset(StructureDataset):
    response = StructureDataset.get("/db/LanguageTable/1")
    assert '<h1>Language ' in response.text
    response = StructureDataset.get("/db/ParameterTable/10")
    assert '<h1>Parameter ' in response.text
    response = StructureDataset.get("/db/ValueTable/1-10")
    assert '<h1>Value ' in response.text
    assert ': 10-20' in response.text
    response = StructureDataset.get("/db/SourceTable/aceto2008")
    assert '@incollection{' in response.text


def test_Dictionary(Dictionary):
    response = Dictionary.get("/db/EntryTable/abwilyep_1")
    assert '<h1>Dictionary entry ' in response.text
    response = Dictionary.get("/db/ExampleTable/XV000001")
    assert '<h1>Example ' in response.text
