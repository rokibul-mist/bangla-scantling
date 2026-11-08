import pymupdf

docs = {
    'Detail_Calculation_Booklet.pdf': 10,
    'Lightship.pdf': 2,
    'Application_Form_Booklet.pdf': 25
}

total_collisions = 0
total_pages = 0

for doc_path, expected_pages in docs.items():
    doc = pymupdf.open(doc_path)
    assert len(doc) == expected_pages, f"{doc_path} has {len(doc)} pages, expected {expected_pages}"
    doc_collisions = 0
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        total_pages += 1
        words = page.get_text("words")
        for i in range(len(words)):
            w1 = words[i]
            r1 = pymupdf.Rect(w1[:4])
            for j in range(i + 1, min(i + 20, len(words))):
                w2 = words[j]
                if w1[5] == w2[5] and w1[6] == w2[6]:
                    continue
                r2 = pymupdf.Rect(w2[:4])
                intersect = r1 & r2
                if not intersect.is_empty and intersect.get_area() > 12:
                    doc_collisions += 1
                    total_collisions += 1
                    print(f"Collision on {doc_path} p{page_idx+1}: '{w1[4]}' & '{w2[4]}' (area: {intersect.get_area():.1f})")
    doc.close()
    print(f"{doc_path}: {expected_pages} pages, {doc_collisions} text collisions")

print(f"\nTotal pages audited: {total_pages}, Total collisions: {total_collisions}")
