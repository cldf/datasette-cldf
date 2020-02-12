
def test_Details(StructureDataset):
    response = StructureDataset.get("/db/LanguageTable/1")
    assert '<h1>Language ' in response.text
    response = StructureDataset.get("/db/ParameterTable/10")
    assert '<h1>Parameter ' in response.text
    response = StructureDataset.get("/db/ValueTable/1-10")
    assert '<h1>Value ' in response.text
