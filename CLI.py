#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact Angle Analysis - Command Line Interface
파일 입출력 및 데이터 처리를 위한 CLI 도구
"""

import argparse
import os
import sys
import json
from pathlib import Path


def validate_path(path):
    """경로 유효성 검사"""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"경로가 존재하지 않습니다: {path}")
    return path


def create_parser():
    """CLI 인자 파서 생성"""
    parser = argparse.ArgumentParser(
        description='Contact Angle Analysis Tool - 파일 입출력 및 데이터 분석',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 데이터 읽기
  python CLI.py read --src ./data --height 5 --surface Glass --degree 45 --viscosity 1000 --number 001
  
  # 윤곽선 데이터 읽기
  python CLI.py read-contour --src ./data --height 5 --surface Glass --degree 45 --viscosity 1000 --number 001
  
  # 이미지 처리
  python CLI.py process --input ./images --output ./results --start 0 --end 100
  
  # 설정 파일로 실행
  python CLI.py --config config.json
        """
    )
    
    # 전역 옵션
    parser.add_argument('--config', type=str, help='설정 파일 경로 (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='상세 출력 모드')
    parser.add_argument('--output-dir', '-o', type=str, default='./output', 
                       help='출력 디렉토리 (기본값: ./output)')
    
    # 서브커맨드 생성
    subparsers = parser.add_subparsers(dest='command', help='실행할 명령')
    
    # 1. read 명령 - 데이터 읽기
    parser_read = subparsers.add_parser('read', help='CSV 데이터 읽기')
    parser_read.add_argument('--src', type=str, required=True, help='소스 디렉토리 경로')
    parser_read.add_argument('--height', type=float, required=True, help='높이 (CM)')
    parser_read.add_argument('--surface', type=str, required=True, help='표면 종류')
    parser_read.add_argument('--degree', type=int, required=True, help='각도')
    parser_read.add_argument('--viscosity', type=int, required=True, help='점도')
    parser_read.add_argument('--number', type=str, required=True, help='실험 번호')
    
    # 2. read-contour 명령 - 윤곽선 데이터 읽기
    parser_contour = subparsers.add_parser('read-contour', help='윤곽선 데이터 읽기')
    parser_contour.add_argument('--src', type=str, required=True, help='소스 디렉토리 경로')
    parser_contour.add_argument('--height', type=float, required=True, help='높이 (CM)')
    parser_contour.add_argument('--surface', type=str, required=True, help='표면 종류')
    parser_contour.add_argument('--degree', type=int, required=True, help='각도')
    parser_contour.add_argument('--viscosity', type=int, required=True, help='점도')
    parser_contour.add_argument('--number', type=str, required=True, help='실험 번호')
    parser_contour.add_argument('--show', action='store_true', help='결과를 화면에 표시')
    
    # 3. process 명령 - 이미지 처리
    parser_process = subparsers.add_parser('process', help='이미지 처리 및 분석')
    parser_process.add_argument('--input', '-i', type=validate_path, required=True, 
                               help='입력 이미지 디렉토리')
    parser_process.add_argument('--output', '-o', type=str, 
                               help='출력 디렉토리 (기본값: 전역 output-dir 사용)')
    parser_process.add_argument('--start', type=int, default=0, help='시작 프레임 번호')
    parser_process.add_argument('--end', type=int, help='종료 프레임 번호')
    parser_process.add_argument('--threshold', type=int, default=128, 
                               help='이진화 임계값 (0-255)')
    parser_process.add_argument('--kernel-size', type=int, default=1, 
                               help='커널 크기')
    
    # 4. analyze 명령 - 접촉각 분석
    parser_analyze = subparsers.add_parser('analyze', help='접촉각 분석')
    parser_analyze.add_argument('--input', '-i', type=validate_path, required=True,
                               help='입력 데이터 경로')
    parser_analyze.add_argument('--method', choices=['diameter', 'contact-angle', 'rim-height'],
                               required=True, help='분석 방법')
    parser_analyze.add_argument('--export', type=str, help='결과 저장 파일명 (CSV)')
    
    # 5. list 명령 - 파일 목록 조회
    parser_list = subparsers.add_parser('list', help='파일 목록 조회')
    parser_list.add_argument('--src', type=validate_path, required=True, 
                            help='검색할 디렉토리')
    parser_list.add_argument('--type', choices=['image', 'video', 'all'], 
                            default='all', help='파일 타입')
    parser_list.add_argument('--export', type=str, help='목록을 파일로 저장')
    
    # 6. convert 명령 - 데이터 변환
    parser_convert = subparsers.add_parser('convert', help='데이터 형식 변환')
    parser_convert.add_argument('--input', '-i', type=validate_path, required=True,
                               help='입력 파일')
    parser_convert.add_argument('--from', dest='from_format', 
                               choices=['contour', 'binary', 'points'],
                               required=True, help='입력 형식')
    parser_convert.add_argument('--to', dest='to_format',
                               choices=['contour', 'binary', 'points', 'csv'],
                               required=True, help='출력 형식')
    parser_convert.add_argument('--output', '-o', type=str, help='출력 파일명')
    
    return parser


def load_config(config_file):
    """JSON 설정 파일 로드"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패: {e}")
        sys.exit(1)


def cmd_read(args):
    """read 명령 실행"""
    import pandas as pd
    
    if args.verbose:
        print(f"데이터 읽기 시작...")
        print(f"  소스: {args.src}")
        print(f"  조건: {args.height}CM_{args.surface}_{args.degree}_{args.viscosity}_{args.number}")
    
    savepath = os.path.join(
        args.src,
        f"{args.height}CM_{args.surface}_{args.degree}_{args.viscosity}_{args.number}",
        "_DATA.csv"
    )
    
    try:
        data = pd.read_csv(savepath)
        print(f"✓ 데이터 로드 완료: {len(data)} 행")
        print(f"  컬럼: {', '.join(data.columns.tolist())}")
        
        if args.verbose:
            print("\n데이터 미리보기:")
            print(data.head())
        
        return data
    except FileNotFoundError:
        print(f"✗ 파일을 찾을 수 없습니다: {savepath}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 데이터 로드 실패: {e}")
        sys.exit(1)


def cmd_read_contour(args):
    """read-contour 명령 실행"""
    import numpy as np
    
    if args.verbose:
        print(f"윤곽선 데이터 읽기 시작...")
    
    temppath = os.path.join(
        args.src,
        f"{args.height}CM_{args.surface}_{args.degree}_{args.viscosity}_{args.number}",
        "Contour Files"
    )
    
    if not os.path.exists(temppath):
        print(f"✗ 윤곽선 디렉토리를 찾을 수 없습니다: {temppath}")
        sys.exit(1)
    
    try:
        file_lst = os.listdir(temppath)
        contours = []
        
        print(f"총 {len(file_lst)} 개의 이미지 처리 중...")
        
        for i in range(len(file_lst)):
            src_path = os.path.join(temppath, f'Imagenumber_{i}')
            if not os.path.exists(src_path):
                continue
                
            file_list2 = os.listdir(src_path)
            temp = []
            
            for k, filename in enumerate(file_list2):
                filepath = os.path.join(src_path, filename)
                try:
                    t = np.load(filepath)
                    temp.append(t)
                except:
                    if args.verbose:
                        print(f"  경고: {filepath} 로드 실패")
            
            if len(temp) > 0:
                contours.append(temp)
            else:
                contours.append(0)
        
        print(f"✓ 윤곽선 데이터 로드 완료: {len(contours)} 프레임")
        return contours
        
    except Exception as e:
        print(f"✗ 윤곽선 데이터 로드 실패: {e}")
        sys.exit(1)


def cmd_list(args):
    """list 명령 실행"""
    if args.verbose:
        print(f"파일 목록 검색 중: {args.src}")
    
    extensions = {
        'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
        'video': ['.mp4', '.avi', '.mov', '.mkv'],
        'all': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.mp4', '.avi', '.mov', '.mkv']
    }
    
    target_ext = extensions[args.type]
    files = []
    
    for root, dirs, filenames in os.walk(args.src):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in target_ext):
                filepath = os.path.join(root, filename)
                files.append(filepath)
    
    print(f"\n✓ 총 {len(files)} 개의 파일 발견:\n")
    for idx, filepath in enumerate(files, 1):
        print(f"  {idx:4d}. {filepath}")
    
    if args.export:
        with open(args.export, 'w', encoding='utf-8') as f:
            f.write('\n'.join(files))
        print(f"\n✓ 목록 저장 완료: {args.export}")
    
    return files


def cmd_process(args):
    """process 명령 실행"""
    output_dir = args.output if args.output else args.output_dir
    
    if args.verbose:
        print(f"이미지 처리 시작...")
        print(f"  입력: {args.input}")
        print(f"  출력: {output_dir}")
        print(f"  프레임: {args.start} ~ {args.end if args.end else 'END'}")
        print(f"  임계값: {args.threshold}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 여기에 실제 이미지 처리 로직 추가
    print(f"✓ 처리 완료 - 결과 저장: {output_dir}")


def cmd_analyze(args):
    """analyze 명령 실행"""
    if args.verbose:
        print(f"분석 시작: {args.method}")
        print(f"  입력: {args.input}")
    
    # 분석 로직 추가
    print(f"✓ {args.method} 분석 완료")


def cmd_convert(args):
    """convert 명령 실행"""
    if args.verbose:
        print(f"데이터 변환: {args.from_format} → {args.to_format}")
        print(f"  입력: {args.input}")
    
    output = args.output if args.output else f"converted.{args.to_format}"
    
    # 변환 로직 추가
    print(f"✓ 변환 완료: {output}")


def main():
    """메인 함수"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 설정 파일이 있으면 로드
    if args.config:
        config = load_config(args.config)
        # config의 값으로 args 업데이트
        for key, value in config.items():
            if not hasattr(args, key) or getattr(args, key) is None:
                setattr(args, key, value)
    
    # 명령이 지정되지 않은 경우
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # 명령에 따른 실행
    try:
        if args.command == 'read':
            cmd_read(args)
        elif args.command == 'read-contour':
            cmd_read_contour(args)
        elif args.command == 'list':
            cmd_list(args)
        elif args.command == 'process':
            cmd_process(args)
        elif args.command == 'analyze':
            cmd_analyze(args)
        elif args.command == 'convert':
            cmd_convert(args)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n\n중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
