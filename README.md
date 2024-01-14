# falconpy

Program to search for specific text in videos/images

## Usage

Search in video
```bash
falconpy -i in.mp4 -s "find me" "hello" "The"
```

Search in image
```bash
falconpy -i in.jpg -s "find me" "hello" "The"
```

Extract all text
```bash
falconpy -i in.jpg -o out.txt
```

Search and extract
```bash
falconpy -i in.jpg -s "find me" "hello" "The" -o out.txt
```
