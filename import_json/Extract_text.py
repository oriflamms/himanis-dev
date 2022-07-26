from bs4 import BeautifulSoup


for image in ["361R", "361V", "362R", "362V", "363R", "363V", "364R", "364V", "365R"]:
    name_file = "/home/reignier/Bureau/Himanis/ANF_FRCHANJJ_JJ_2/FRCHANJJ_JJ081_0" + image + "_A.xml"
    with open(name_file, 'r') as f:
        doc = f.read()
    soup = BeautifulSoup(doc, features="xml")
    Acts = soup.find_all('TextRegion')
    for act in Acts:
        print(image)
        texts = act.find_all('TextLine')
        for text in texts:
            print("\"" + text.Unicode.get_text() + '\",')