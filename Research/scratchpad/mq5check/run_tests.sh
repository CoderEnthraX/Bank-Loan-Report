#!/bin/bash
# Runs every tests/*.mq5. First line of each file: "// EXPECT: error|warning <text>" or "// EXPECT: clean".
HERE="$(cd "$(dirname "$0")" && pwd)"
pass=0; fail=0
for f in "$HERE"/tests/*.mq5; do
  name=$(basename "$f" .mq5)
  spec=$(head -1 "$f" | sed -n 's#^// EXPECT: *##p')
  kind=${spec%% *}; text=${spec#"$kind"}; text=${text# }
  out=$(python3 -I "$HERE/mq5check.py" "$f" 2>&1)
  res=$(echo "$out" | grep '^RESULT:')
  ne=$(echo "$res" | sed -E 's/RESULT: ([0-9]+) errors.*/\1/'); nw=$(echo "$res" | sed -E 's/.* ([0-9]+) warnings/\1/')
  ok=0
  case "$kind" in
    clean)   [ "$ne" = 0 ] && [ "$nw" = 0 ] && ok=1 ;;
    error)   [ "$ne" -gt 0 ] && echo "$out" | grep ': error:' | grep -qF -- "$text" && ok=1 ;;
    warning) [ "$ne" = 0 ] && [ "$nw" -gt 0 ] && echo "$out" | grep ': warning:' | grep -qF -- "$text" && ok=1 ;;
  esac
  if [ $ok = 1 ]; then echo "PASS $name  ($res)"; pass=$((pass+1)); else echo "FAIL $name  expected: $spec"; echo "$out" | sed 's/^/     /'; fail=$((fail+1)); fi
done
echo "== $pass passed, $fail failed"
[ $fail = 0 ]
