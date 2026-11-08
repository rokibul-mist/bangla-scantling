import matplotlib.mathtext as mathtext
import io
from PIL import Image

latex_samples = [
    r'C_w = 0.08 \cdot k_t \cdot \sqrt{L}',
    r'M_{sw} = 0.06 \cdot C_b \cdot L^2 \cdot B \cdot (d + 0.02 L)',
    r'M_{w,hog} = 0.19 \cdot C_w \cdot L^2 \cdot B \cdot C_b',
    r'M_{w,sag} = 0.11 \cdot C_w \cdot L^2 \cdot B \cdot (C_b + 0.70)',
    r'M_{total,hog} = M_{sw} + M_{w,hog}',
    r'M_{total,sag} = M_{sw} + M_{w,sag}',
    r'M_{design} = \max(M_{total,hog}, M_{total,sag})',
    r'Q_{design} = \frac{2.5 \cdot M_{design}}{L}',
    r'Z_1 = \frac{M_{design} \times 10^3}{\sigma_{allowable}} \quad (\sigma_{allowable} = 130\ \mathrm{N/mm}^2)',
    r'Z_2 = 1.75 \cdot k_t \cdot L^2 \cdot B \cdot (C_b + 0.70)',
    r'Z_{req} = \max(Z_1, Z_2)',
    r'I_{req} = 3.0 \cdot Z_{req} \cdot L \times 10^{-2}',
    r'M_{perm} = \sigma_{allowable} \cdot Z_{actual} \times 10^{-3}'
]

for s in latex_samples:
    buf = io.BytesIO()
    mathtext.math_to_image(f"${s}$", buf, dpi=200, format='png')
    img = Image.open(buf)
    print("Rendered OK:", s[:35], "Size:", img.size)

print("ALL LATEX EQUATIONS RENDERED PERFECTLY!")
