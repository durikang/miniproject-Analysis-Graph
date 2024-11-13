import os
import csv

class TxtToCsvConverter:
    def __init__(self, bs_input_dir, is_input_dir, bs_output_dir, is_output_dir):
        self.bs_input_dir = bs_input_dir
        self.is_input_dir = is_input_dir
        self.bs_output_dir = bs_output_dir
        self.is_output_dir = is_output_dir

        # 결과 폴더 생성
        os.makedirs(self.bs_output_dir, exist_ok=True)
        os.makedirs(self.is_output_dir, exist_ok=True)

    def convert_all_txt_files(self):
        # BS_raw 디렉토리의 .txt 파일을 변환하여 BS 디렉토리에 저장
        self.convert_directory(self.bs_input_dir, self.bs_output_dir)
        # IS_graph 디렉토리의 .txt 파일을 변환하여 IS 디렉토리에 저장
        self.convert_directory(self.is_input_dir, self.is_output_dir)

    def convert_directory(self, input_dir, output_dir):
        # 입력 디렉토리에서 모든 .txt 파일을 변환
        for filename in os.listdir(input_dir):
            if filename.endswith(".txt"):
                input_file_path = os.path.join(input_dir, filename)
                self.convert_file_to_csv(input_file_path, output_dir)

    def convert_file_to_csv(self, input_file_path, output_dir):
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_csv_path = os.path.join(output_dir, f"{base_name}(수정).csv")

        try:
            with open(input_file_path, 'r', encoding='cp949') as infile, open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as outfile:
                reader = csv.reader(infile, delimiter='\t')
                writer = csv.writer(outfile)
                for row in reader:
                    writer.writerow(row)
            print(f"{output_csv_path}로 CSV 변환 완료")
        except UnicodeDecodeError:
            print(f"파일 인코딩 오류 발생: {input_file_path}")
