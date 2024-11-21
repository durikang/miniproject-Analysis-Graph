import os
import csv
import traceback
from charset_normalizer import detect  # 인코딩 감지 라이브러리


class TxtToCsvConverter:
    def __init__(self, bs_raw_path, is_raw_path, bs_output_path, is_output_path):
        self.bs_raw_path = bs_raw_path
        self.is_raw_path = is_raw_path
        self.bs_output_path = bs_output_path
        self.is_output_path = is_output_path

    def convert_all(self, progress_callback=None):
        try:
            total_files = (
                len(self._get_txt_files(self.bs_raw_path)) +
                len(self._get_txt_files(self.is_raw_path))
            )
            converted_files = 0

            # BS 원본 경로 파일 변환
            for txt_file in self._get_txt_files(self.bs_raw_path):
                self.convert_file_to_csv(txt_file, self.bs_output_path)
                converted_files += 1
                if progress_callback:
                    progress_callback(converted_files, total_files)

            # IS 원본 경로 파일 변환
            for txt_file in self._get_txt_files(self.is_raw_path):
                self.convert_file_to_csv(txt_file, self.is_output_path)
                converted_files += 1
                if progress_callback:
                    progress_callback(converted_files, total_files)

        except Exception as e:
            print(f"[ERROR] Conversion failed: {str(e)}")
            traceback.print_exc()
            raise e

    def convert_file_to_csv(self, txt_file, output_dir):
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            base_name = os.path.basename(txt_file)
            csv_file_name = os.path.splitext(base_name)[0] + ".csv"
            csv_file_path = os.path.join(output_dir, csv_file_name)

            # 인코딩 감지
            with open(txt_file, "rb") as f:
                raw_data = f.read()
                detected = detect(raw_data)
                encoding = detected["encoding"]
                print(f"[INFO] Detected encoding for {txt_file}: {encoding}")

            # UTF-8(BOM) 여부 확인
            if encoding.lower() == "utf-8-sig":
                print(f"[INFO] File {txt_file} is already UTF-8(BOM), skipping re-encoding.")

            # 파일 열기
            with open(txt_file, "r", encoding=encoding) as infile:
                first_line = infile.readline()
                delimiter = self._detect_delimiter(first_line)
                print(f"[INFO] Detected delimiter for {txt_file}: {repr(delimiter)}")

                # 데이터를 UTF-8(BOM)으로 변환하여 CSV로 저장
                with open(csv_file_path, "w", newline="", encoding="utf-8-sig") as outfile:
                    csv_writer = csv.writer(outfile)

                    # 첫 줄 변환 후 기록
                    csv_writer.writerow(first_line.strip().split(delimiter))

                    # 나머지 줄 변환 후 기록
                    for line in infile:
                        csv_writer.writerow(line.strip().split(delimiter))

            print(f"[INFO] Converted: {txt_file} -> {csv_file_path}")

        except Exception as e:
            print(f"[ERROR] Failed to convert {txt_file} to CSV: {str(e)}")
            traceback.print_exc()
            raise e

    @staticmethod
    def _detect_delimiter(line):
        """
        첫 줄을 기준으로 구분자를 감지
        :param line: 파일의 첫 줄
        :return: 구분자 문자열
        """
        if "\t" in line:
            return "\t"
        elif "," in line:
            return ","
        else:
            raise ValueError("Unable to detect delimiter in the file.")

    @staticmethod
    def _get_txt_files(directory):
        if not os.path.exists(directory):
            print(f"[WARNING] Directory does not exist: {directory}")
            return []
        return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".txt")]
