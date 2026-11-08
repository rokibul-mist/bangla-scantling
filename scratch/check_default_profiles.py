from app.domain.catalog.structural_catalog import STRUCTURAL_MEMBERS

for m in STRUCTURAL_MEMBERS:
    if m['id'] in ['stiff_centre_keelson', 'stiff_side_keelson', 'stiff_floor_single', 'stiff_centre_girder', 'stiff_solid_floor', 'stiff_deck_web_beam', 'stiff_deck_girder']:
        print(f"{m['id']}: default_profile = {m.get('default_profile')}")
