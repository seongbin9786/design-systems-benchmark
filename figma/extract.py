#!/usr/bin/env python3
"""Figma 파일에서 컴포넌트/Variables/Styles 추출"""
import json, sys, os, urllib.request

FIGMA_TOKEN = os.environ["FIGMA_TOKEN"]
BASE = "https://api.figma.com/v1"
OUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUT_DIR, exist_ok=True)

FILES = {
    "carbon": "qitdRY9kvVF80IwfFOd6dh",
    "spectrum": "VN27jZQKq2YTR9kavQH27p",
    "material3": "jFqFUx2lt37lQJX6v80Xpc",
    "fluent2": "zh53bUlnsBwTu61rP9Wc1q",
}

def api(path):
    req = urllib.request.Request(f"{BASE}{path}", headers={"X-Figma-Token": FIGMA_TOKEN})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

def extract_components(node, page_name, results):
    """재귀적으로 COMPONENT / COMPONENT_SET 노드 추출"""
    ntype = node.get("type", "")
    if ntype in ("COMPONENT", "COMPONENT_SET"):
        info = {
            "id": node.get("id"),
            "name": node.get("name"),
            "type": ntype,
            "page": page_name,
        }
        # COMPONENT_SET의 경우 variant 정보
        if ntype == "COMPONENT_SET":
            props = node.get("componentPropertyDefinitions", {})
            info["variant_properties"] = {
                k: {"type": v.get("type"), "values": v.get("variantOptions", [])}
                for k, v in props.items()
                if v.get("type") == "VARIANT"
            }
            # 자식 COMPONENT 수
            children = node.get("children", [])
            info["variant_count"] = len([c for c in children if c.get("type") == "COMPONENT"])
        results.append(info)
    for child in node.get("children", []):
        extract_components(child, page_name, results)

def extract_variables(file_key, name):
    """Variables 추출"""
    try:
        data = api(f"/files/{file_key}/variables/local")
        meta = data.get("meta", {})
        collections = meta.get("variableCollections", {})
        variables = meta.get("variables", {})
        
        result = {
            "collections": {},
            "variables_by_collection": {},
            "total_variables": len(variables),
        }
        for cid, col in collections.items():
            result["collections"][cid] = {
                "name": col.get("name"),
                "modes": [m.get("name") for m in col.get("modes", [])],
            }
            result["variables_by_collection"][col.get("name", cid)] = []
        
        for vid, var in variables.items():
            col_id = var.get("variableCollectionId", "")
            col_name = collections.get(col_id, {}).get("name", col_id)
            entry = {
                "name": var.get("name"),
                "type": var.get("resolvedType"),
                "description": var.get("description", ""),
            }
            if col_name in result["variables_by_collection"]:
                result["variables_by_collection"][col_name].append(entry)
        
        return result
    except Exception as e:
        return {"error": str(e)}

def extract_styles(file_key, name):
    """Styles 추출"""
    try:
        data = api(f"/files/{file_key}/styles")
        styles = data.get("meta", {}).get("styles", [])
        return {
            "total": len(styles),
            "by_type": {},
            "styles": [{"name": s.get("name"), "type": s.get("style_type"), "key": s.get("key")} for s in styles],
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    for name, file_key in FILES.items():
        print(f"\n{'='*60}")
        print(f"  {name} ({file_key})")
        print(f"{'='*60}")
        
        # 1. 파일 구조 (depth 제한 없이 전체 트리)
        print(f"  [1/3] 노드 트리 가져오는 중...")
        try:
            file_data = api(f"/files/{file_key}")
            pages = file_data.get("document", {}).get("children", [])
            
            components = []
            for page in pages:
                extract_components(page, page.get("name", ""), components)
            
            comp_sets = [c for c in components if c["type"] == "COMPONENT_SET"]
            comp_singles = [c for c in components if c["type"] == "COMPONENT"]
            
            print(f"  페이지: {len(pages)}개")
            print(f"  COMPONENT_SET: {len(comp_sets)}개")
            print(f"  COMPONENT (단일): {len(comp_singles)}개")
            print(f"  총 variant 수: {sum(c.get('variant_count', 0) for c in comp_sets)}")
            
            # 컴포넌트 이름 목록
            comp_names = sorted(set(c["name"] for c in comp_sets))
            print(f"  COMPONENT_SET 이름 (처음 20개): {comp_names[:20]}")
            
            # 결과 저장
            with open(f"{OUT_DIR}/{name}-components-extracted.json", "w") as f:
                json.dump({"component_sets": comp_sets, "single_components": comp_singles, "page_count": len(pages)}, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"  노드 트리 에러: {e}")
        
        # 2. Variables
        print(f"  [2/3] Variables 가져오는 중...")
        vars_data = extract_variables(file_key, name)
        if "error" not in vars_data:
            print(f"  총 Variables: {vars_data['total_variables']}개")
            for col_name, col_vars in vars_data.get("variables_by_collection", {}).items():
                print(f"    컬렉션 '{col_name}': {len(col_vars)}개")
        else:
            print(f"  Variables 에러: {vars_data['error']}")
        
        with open(f"{OUT_DIR}/{name}-variables.json", "w") as f:
            json.dump(vars_data, f, indent=2, ensure_ascii=False)
        
        # 3. Styles
        print(f"  [3/3] Styles 가져오는 중...")
        styles_data = extract_styles(file_key, name)
        if "error" not in styles_data:
            print(f"  총 Styles: {styles_data['total']}개")
            type_counts = {}
            for s in styles_data.get("styles", []):
                t = s.get("type", "UNKNOWN")
                type_counts[t] = type_counts.get(t, 0) + 1
            for t, c in sorted(type_counts.items()):
                print(f"    {t}: {c}개")
        else:
            print(f"  Styles 에러: {styles_data['error']}")
        
        with open(f"{OUT_DIR}/{name}-styles.json", "w") as f:
            json.dump(styles_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
