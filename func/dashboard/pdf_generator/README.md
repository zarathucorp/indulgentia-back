# pdf_generator



## Tech stack

- Ubuntu 22.04
- Python
  - Pillow
  - PdfMerger
  - subprocess
- Libreoffice



## Feature

### Available file

- doc / docx
- ppt / pptx
- xls / xlsx
- hwp / hwpx (WIP, 이미지 크기 속성 버그)
- image(jpg, jpeg, bmp, png)
- pdf



## Install

### Libreoffice

```bash	
sudo apt-get update

sudo apt install libreoffice

# libreoffice 설치 테스트
libreoffice --version

# 한글 폰트 설치
sudo apt install -y language-pack-ko fonts-nanum-* fontconfig
fc-cache -f -v
# 한글 테스트
touch 한글테스트

# 한글 extension 설치
wget https://github.com/ebandal/H2Orestart/releases/latest/download/H2Orestart.oxt
sudo unopkg add --shared H2Orestart.oxt
```

