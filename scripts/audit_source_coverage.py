#!/usr/bin/env python3
"""Audit complete OCR partition coverage and machine-only extraction scope."""
from __future__ import annotations
import argparse,csv,json,re,unicodedata
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]; FULL_OCR=ROOT/'data/source/ocr/ortega1888_full_ocr.txt'; CANDIDATES=ROOT/'data/lexicon/candidates.csv'; OUTPUT=ROOT/'reports/source_coverage.json'
BOUNDARY_MARKERS={'alphabetical_lexicon_body':'A., denotando la persona que padece','numerals_appendix':'Cuenta para contar todo lo numerable','irregular_verbs_particles_appendix':'Por último pondrá aqui algunos verbos irregulares'}
PARTITION_PATHS={'preliminary_matter':ROOT/'data/grammar/preliminary_ocr.txt','alphabetical_lexicon_body':ROOT/'data/source/ocr/lexicon_body_raw.txt','numerals_appendix':ROOT/'data/appendices/numerals_ocr.txt','irregular_verbs_particles_appendix':ROOT/'data/appendices/irregular_verbs_particles_ocr.txt'}
def norm_key(text:str)->str:
    normalized=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower(); return re.sub(r'[^a-z0-9]','',normalized)
def find_boundary(lines:list[str],marker:str)->int:
    key=norm_key(marker)
    for index,line in enumerate(lines):
        if key in norm_key(line): return index
    raise ValueError(f'source boundary marker not found: {marker}')
def locate_partition_ranges(lines:list[str])->dict[str,tuple[int,int]]:
    start=find_boundary(lines,BOUNDARY_MARKERS['alphabetical_lexicon_body']); numerals=find_boundary(lines,BOUNDARY_MARKERS['numerals_appendix']); irregular=find_boundary(lines,BOUNDARY_MARKERS['irregular_verbs_particles_appendix'])
    if not (0<=start<numerals<irregular<=len(lines)): raise ValueError(f'source partition boundaries are not strictly ordered: alphabetical={start+1}, numerals={numerals+1}, irregular={irregular+1}')
    return {'preliminary_matter':(0,start),'alphabetical_lexicon_body':(start,numerals),'numerals_appendix':(numerals,irregular),'irregular_verbs_particles_appendix':(irregular,len(lines))}
def render_partition(lines:list[str],start:int,end:int)->str: return '\n'.join(lines[start:end]).rstrip()+'\n'
def verify_partition_files(lines:list[str],ranges:dict[str,tuple[int,int]],partition_paths:dict[str,Path])->None:
    if set(partition_paths)!=set(ranges): raise ValueError(f'partition path contract mismatch: missing={sorted(set(ranges)-set(partition_paths))}, extra={sorted(set(partition_paths)-set(ranges))}')
    for partition_id,(start,end) in ranges.items():
        path=partition_paths[partition_id]
        if not path.is_file(): raise ValueError(f'derived partition file missing: {path}')
        if path.read_text(encoding='utf-8')!=render_partition(lines,start,end): raise ValueError(f'derived partition drift for {partition_id}: {path} no longer matches the full OCR slice')
def load_candidates(path:Path)->list[dict[str,str]]:
    if not path.is_file(): raise ValueError(f'candidate inventory missing: {path}')
    with path.open('r',encoding='utf-8-sig',newline='') as handle: return list(csv.DictReader(handle))
def verify_candidate_scope(candidates:list[dict[str,str]],body_range:tuple[int,int])->dict[str,Any]:
    body_start,body_end=body_range; first_allowed_line,last_allowed_line=body_start+1,body_end; orders=[]
    for row in candidates:
        candidate_id=row.get('candidate_id','<unknown>')
        try: order=int(row['order']); line_start=int(row['source_ocr_line_start']); line_end=int(row['source_ocr_line_end'])
        except (KeyError,TypeError,ValueError) as exc: raise ValueError(f'candidate {candidate_id} has invalid order or OCR line bounds') from exc
        if line_start>line_end: raise ValueError(f'candidate {candidate_id} has inverted OCR line bounds')
        if line_start<first_allowed_line or line_end>last_allowed_line: raise ValueError(f'candidate {candidate_id} escapes alphabetical body lines {first_allowed_line}-{last_allowed_line}: {line_start}-{line_end}')
        orders.append(order)
    if orders and sorted(orders)!=list(range(1,len(orders)+1)): raise ValueError('candidate order is not a complete 1..N sequence')
    return {'candidate_total':len(candidates),'candidate_order_min':min(orders) if orders else None,'candidate_order_max':max(orders) if orders else None,'all_candidates_within_alphabetical_body':True}
def _display_path(path:Path)->str:
    try: return path.relative_to(ROOT).as_posix()
    except ValueError: return path.as_posix()
def build_coverage_report(full_ocr_path:Path=FULL_OCR,candidates_path:Path=CANDIDATES,partition_paths:dict[str,Path]|None=None)->dict[str,Any]:
    if not full_ocr_path.is_file(): raise ValueError(f'full OCR witness missing: {full_ocr_path}')
    lines=full_ocr_path.read_text(encoding='utf-8').splitlines()
    if not lines: raise ValueError('full OCR witness is empty')
    ranges=locate_partition_ranges(lines); paths=partition_paths or PARTITION_PATHS; verify_partition_files(lines,ranges,paths); candidates=load_candidates(candidates_path); candidate_scope=verify_candidate_scope(candidates,ranges['alphabetical_lexicon_body'])
    ordered_ids=['preliminary_matter','alphabetical_lexicon_body','numerals_appendix','irregular_verbs_particles_appendix']; previous_end=0; partitions=[]
    for partition_id in ordered_ids:
        start,end=ranges[partition_id]
        if start!=previous_end: raise ValueError(f'source coverage gap or overlap before {partition_id}: expected start {previous_end}, got {start}')
        previous_end=end; record={'partition_id':partition_id,'path':_display_path(paths[partition_id]),'source_ocr_line_start':start+1 if end>start else None,'source_ocr_line_end':end if end>start else None,'line_total':end-start}
        if partition_id=='alphabetical_lexicon_body': record.update({'content_role':'alphabetical_vocabulary_body','structured_status':'machine_candidates','machine_candidate_total':len(candidates)})
        elif partition_id=='numerals_appendix': record.update({'content_role':'lexical_numeral_appendix','structured_status':'raw_ocr_plus_machine_navigation_inventory'})
        elif partition_id=='irregular_verbs_particles_appendix': record.update({'content_role':'lexical_grammatical_appendix','structured_status':'raw_ocr_plus_machine_navigation_inventory'})
        else: record.update({'content_role':'preliminary_matter','structured_status':'raw_ocr_context'})
        partitions.append(record)
    if previous_end!=len(lines): raise ValueError(f'source coverage ends at OCR line {previous_end}, but full witness has {len(lines)} lines')
    return {'artifact_type':'source_coverage_audit','source_witness_id':'ORTEGA1888-TEPIC-IA','machine_generated':True,'human_verified':False,'full_ocr_path':_display_path(full_ocr_path),'full_ocr_line_total':len(lines),'partitions':partitions,'coverage':{'contiguous':True,'gap_count':0,'overlap_count':0,'derived_partition_files_match_full_ocr':True},'candidate_scope':candidate_scope,'lexical_scope':{'alphabetical_body_structured_as_machine_candidates':True,'numerals_appendix_structured':False,'irregular_verbs_particles_appendix_structured':False,'witness_lexical_content_fully_structured':False,'numerals_appendix_machine_inventory':True,'irregular_verbs_particles_appendix_machine_inventory':True,'human_review_stage':False},'scope_note':'ORT1888-cand covers only the alphabetical vocabulary body. The two appendices retain complete raw OCR and receive separate machine navigation inventories; they are not folded into the alphabetical candidate namespace.'}
def main()->None:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--full-ocr',type=Path,default=FULL_OCR); parser.add_argument('--candidates',type=Path,default=CANDIDATES); parser.add_argument('--output',type=Path,default=OUTPUT); args=parser.parse_args()
    try: report=build_coverage_report(args.full_ocr,args.candidates)
    except ValueError as exc: raise SystemExit(f'source coverage audit failed: {exc}') from exc
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(f"source coverage ok: {report['full_ocr_line_total']} OCR lines; {report['candidate_scope']['candidate_total']} alphabetical candidates")
if __name__=='__main__': main()
