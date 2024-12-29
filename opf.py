# """
# <?xml version='1.0' encoding='utf-8'?>
# <ns0:package xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" version="2.0">
# 	<ns0:metadata>
# 		<dc:title>Narrenturm</dc:title>
# 		<dc:creator ns0:role="aut">Andrzej Sapkowski</dc:creator>
# 		<dc:creator ns0:role="nrt">zespół lektorów</dc:creator>
# 		<dc:date />
# 		<dc:publisher />
# 		<dc:identifier ns0:scheme="ISBN" />
# 		<dc:description>
# Świat nie zginął i nie spłonął. Przynajmniej nie cały.
# Ale i tak było wesoło.
# [...]
# Przed nami jeszcze dwa tomy trylogii. </dc:description>
# 		<dc:language>pol</dc:language>
# 		<ns0:meta name="calibre:series" content="Trylogia husycka" />
# 		<ns0:meta name="calibre:series_index" content="1" />
# 		<dc:subject>fantasy</dc:subject>
# 		<dc:subject>science fiction</dc:subject>
# 		<dc:tag>Nagroda Zajdla - zwycięzca</dc:tag>
# 		<dc:tag>Husyci</dc:tag>
# 		<dc:tag>Reynewen</dc:tag>
# 		<dc:tag>czarna magia</dc:tag>
# 		<dc:tag>biała magia</dc:tag>
# 		<dc:tag>Śląsk</dc:tag>
# 	</ns0:metadata>
# </ns0:package>
# """


# "id": json_data["id"],
# "title": json_data["title"],
# "author": "",
# "authors": [],
# "narrator": "",
# "narrators": [],
# "series": "",
# "series_count": 0,
# "series_num": 0,
# "genres": [],
# "cover": json_data["cover_url"],
# "tags": [],
# "desription": re.sub(CLEANR, "", json_data["html_annotation"]),
# "isbn": json_data["isbn"],
# "publishedYear": json_data["publication_date"].split("-")[0],
# "publishedDate": json_data["publication_date"],
# "uuid": json_data["uuid"],


def xml_element(name, value, prefix="dc:"):
    return f"   <{prefix}{name}>{value}</{prefix}{name}>\n"


def book_info_to_xml(book_info):
    xml = '<?xml version="1.0" encoding="utf-8"?>\
    <ns0:package xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" version="2.0">\
	<ns0:metadata>'

    for key in book_info:
        if type(book_info[key]) == type([]):
            for value in book_info[key]:
                xml_key = key
                if 's' in xml_key[-1]:
                    xml_key = xml_key[:-1]
                xml += xml_element(xml_key, value)
        else:
            xml += xml_element(key, book_info[key])

    xml += "</ns0:metadata> </ns0:package>"

    return xml
