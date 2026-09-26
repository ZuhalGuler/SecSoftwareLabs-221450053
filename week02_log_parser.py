from pathlib import Path
from collections import Counter
 
LOG = Path(__file__).parents[1] / "datasets" / "auth.log"
 
def parse_line(line: str) -> dict: 
    parts = line.split() 
    timestamp=parts[0] 
    data={"timestamp": timestamp} 
    for item in parts[1:]: 
        key, value = item.split("=") 
        data[key] = value 
    return data 
 
   
 
def main(): 
    status_counts = Counter()
    failed_ips = Counter()

    with LOG.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            record = parse_line(line)

            status_counts[record["status"]] += 1

            if record["status"] == "FAILED":
                failed_ips[record["src_ip"]] += 1

    print("Status counts:", dict(status_counts))
    print("Top failed IP:", failed_ips.most_common(1)[0])
 
if __name__ == "__main__": 
    main()

