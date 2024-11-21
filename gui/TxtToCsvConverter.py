import os
import pandas as pd
from charset_normalizer import detect
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

class TxtToCsvConverter:
    def __init__(self, bs_raw_path, is_raw_path, bs_output_path, is_output_path, expected_fields):
        self.bs_raw_path = bs_raw_path
        self.is_raw_path = is_raw_path
        self.bs_output_path = bs_output_path
        self.is_output_path = is_output_path
        self.expected_fields = expected_fields  # 예상 필드 개수

    def convert_all(self, progress_callback=None):
        """모든 텍스트 파일을 CSV로 변환"""
        try:
            all_txt_files = self._get_txt_files(self.bs_raw_path) + self._get_txt_files(self.is_raw_path)
            total_files = len(all_txt_files)
            converted_files = 0

            # 멀티스레드 방식으로 변환 실행
            with ThreadPoolExecutor() as executor:
                future_to_file = {executor.submit(self.convert_file_to_csv, txt_file): txt_file for txt_file in all_txt_files}

                for future in as_completed(future_to_file):
                    try:
                        future.result()
                        converted_files += 1
                        if progress_callback:
                            progress_callback(converted_files, total_files)
                    except Exception as e:
                        print(f"[ERROR] Failed during file conversion: {e}")

        except Exception as e:
            print(f"[ERROR] Conversion failed: {e}")

    def convert_file_to_csv(self, txt_file):
        try:
            # 출력 디렉토리 결정
            output_dir = self.bs_output_path if txt_file.startswith(self.bs_raw_path) else self.is_output_path
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            base_name = os.path.basename(txt_file)
            csv_file_name = os.path.splitext(base_name)[0] + ".csv"
            csv_file_path = os.path.join(output_dir, csv_file_name)

            # 인코딩 감지
            encoding = self.detect_encoding(txt_file)

            # 구분자 감지
            with open(txt_file, "r", encoding=encoding) as infile:
                first_line = infile.readline()
                delimiter = self._detect_delimiter(first_line)

            # 데이터 정리
            cleaned_lines = self.clean_malformed_lines(txt_file, delimiter, self.expected_fields, encoding)

            # DataFrame으로 변환 (첫 번째 열을 index로 변환하지 않음)
            data = [line.split(delimiter) for line in cleaned_lines]
            df = pd.DataFrame(data)

            # CSV 저장 (index를 저장하지 않음)
            df.to_csv(csv_file_path, index=False, header=False, encoding="utf-8-sig")

            print(f"[INFO] Converted: {txt_file} -> {csv_file_path}")

        except Exception as e:
            print(f"[ERROR] Failed to convert {txt_file}: {e}")

    def detect_encoding(self, file_path):
        """cp949로 우선 처리하고 실패하면 charset_normalizer로 감지"""
        try:
            with open(file_path, "r", encoding="cp949") as f:
                f.readline()  # cp949로 읽기 시도
            print(f"[INFO] Encoding detected as cp949 for {file_path}")
            return "cp949"
        except Exception:
            print(f"[WARNING] cp949 failed for {file_path}. Detecting with charset_normalizer.")
            with open(file_path, "rb") as f:
                raw_data = f.read()
                detected = detect(raw_data)
                encoding = detected["encoding"]
                print(f"[INFO] Detected encoding: {encoding} for {file_path}")
                return encoding

    def clean_malformed_lines(self, file_path, delimiter, expected_fields, encoding):
        """문제 발생 시 예외를 처리하고, 원본 데이터를 유지"""
        clean_lines = []
        try:
            with open(file_path, "r", encoding=encoding) as file:
                for line in file:
                    # 예상 필드 개수와 상관없이 데이터를 추가
                    clean_lines.append(line.strip())
        except Exception as e:
            # 문제 발생 시 스택 트레이스를 기록
            print(f"[ERROR] An error occurred while processing the file: {file_path}")
            print(traceback.format_exc())
        return clean_lines

    @staticmethod
    def _detect_delimiter(line):
        """구분자 감지"""
        if "\t" in line:
            return "\t"
        elif "," in line:
            return ","
        else:
            raise ValueError("Unable to detect delimiter in the file.")

    @staticmethod
    def _get_txt_files(directory):
        """디렉토리 내의 텍스트 파일 리스트 반환"""
        if not os.path.exists(directory):
            print(f"[WARNING] Directory does not exist: {directory}")
            return []
        return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".txt")]
