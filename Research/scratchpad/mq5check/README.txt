mq5check - offline MQL5 compile checker (MetaEditor is not available here)
=========================================================================

HOW TO RUN
  python3 -I mq5check.py path/to/Expert.mq5          # diagnostics + "RESULT: N errors, M warnings" (exit 1 if N>0)
  python3 -I mq5check.py --cpp out.cpp File.mq5      # also keep the generated C++
  python3 -I mq5check.py --raw File.mq5              # also print raw clang output
  ./run_tests.sh                                     # PASS/FAIL per tests/*.mq5 (first line: "// EXPECT: error|warning <text>" or "// EXPECT: clean")
Needs only python3 and clang++ (tested with clang 18). Files are in this directory: mq5check.py, mql5shim.h, tests/.

HOW IT WORKS
  1. mq5check.py rewrites the .mq5 into C++ with the SAME line numbers (#line directives; local #include "x.mqh" files are
     inlined with their own #line), so every diagnostic points at the original .mq5 line.
  2. clang++ -std=c++17 -fsyntax-only type-checks it against mql5shim.h, a declaration-only model of the MQL5 API.
  3. clang messages are re-worded in MetaEditor style ("'x' - undeclared identifier", "possible loss of data due to type
     conversion", "implicit conversion from 'number' to 'string'", "declaration of 'x' hides global declaration",
     "variable 'x' not initialized", ...); the original clang text and flag stay in [clang: ...] for reference.
  Translation done by the preprocessor: #property dropped; `input group "..."` dropped; `input T x = v;` / `sinput` -> `const T x = v;`
  (assigning an input is an error); D'..' and C'..' literals -> numbers; every "string literal" -> "..."_mq (shim string type);
  `long` -> 64-bit type (C++ `long` differs); `T a[];` / `T &a[]` -> MqlArr<T> / ArrayView<T> (works with ArrayResize, ArraySize,
  ArrayInitialize, ArrayFree, ArrayRemove, ...; static arrays `T a[N]` stay C arrays and ArraySize works on them);
  `(string)x` explicit cast -> no warning; obj.member on object POINTERS (MQL5 has no ->) -> mq_dot(obj).member;
  C++-only keywords that are legal MQL5 identifiers are renamed; the signatures of OnTick/OnDeinit/OnTimer/OnTrade/
  OnTradeTransaction/OnChartEvent/OnTester are checked by assigning them to the exact expected function-pointer type.

WHAT IS COVERED (MetaEditor ERRORS)
  undeclared identifiers / functions / members, missing ';' and other syntax errors, wrong argument count or types (incl. enum
  families: e.g. ObjectSetDouble with an integer OBJPROP_*), assigning to an input or const, string/number/array type
  mismatches, redefinition in the same scope, void/non-void return misuse, constant array index out of range, constant zero
  divide, wrong event-handler signature, use of functions that do not exist in MQL5 (e.g. ObjectSetText, OrderSelect(int,..)
  MQL4-style calls fail the overload check).
WHAT IS COVERED (WARNINGS)
  double->int / long->int / int->short|char ("possible loss of data"), number->string implicit conversion (string s = 5;
  "a" + 5; s += 3; passing a number to a string parameter), local hiding a global/outer local/parameter, possibly
  uninitialised variable, signed/unsigned comparison, not all control paths return a value, expression without effect.
  NOT reported (MetaEditor does not either): unused variables/parameters.
API in the shim: types, math (MathMax/MathMin return the higher of the two argument types), strings, time, MqlDateTime/MqlRates/
  MqlTick/MqlTrade*, series (iHigh.., CopyRates, CopyBuffer, iMA/iATR/...), Symbol/Account/Position/Order/History/Deal functions and
  all their enums, chart + object API (ObjectCreate with 1-3 points, ObjectSet/Get Integer/Double/String with and without
  modifier, ObjectMove, ObjectFind, ObjectDelete, ObjectsDeleteAll (2 overloads), ChartGetInteger/Redraw, TextSetFont/TextGetSize,
  OBJ_*, OBJPROP_*, STYLE_*, CORNER_*, ANCHOR_*, BORDER_*, all clr* web colours, MQL_*, TERMINAL_*, CHART_*, REASON_*, INIT_*,
  TIME_*, FW_*), timers/events, GlobalVariable*, and the classes CTrade, CSymbolInfo, CPositionInfo, CDealInfo, COrderInfo,
  CAccountInfo (subset of methods; add missing ones to mql5shim.h when MetaEditor knows them).

KNOWN GAPS / DIFFERENCES (what MetaEditor would catch or decide differently)
  - The shim is written from memory of the MQL5 docs, not extracted from MetaEditor: a missing API or a wrong signature shows up
    as a false "undeclared identifier"/"wrong parameters"; an over-permissive signature hides a real error. Add/fix in mql5shim.h.
    Other <...> includes (Arrays/, Generic/, Indicators/, Canvas/ ...) are not modelled (warning printed; symbols then undeclared).
  - Integer -> enum implicit conversion is an error in C++ but normally accepted by MQL5. Such diagnostics are reported as
    WARNINGS ("implicit integer->enum conversion ... verify"), never as errors. Enum-to-different-enum stays an error.
  - Implicit string -> number conversion (int x = "5";) is an error here (MQL5 only warns); explicit casts (int)s work.
  - Whether MetaEditor warns for long->double, ulong->long, int->uint conversions is not modelled (long->double is silenced).
  - Class objects are not auto-converted to pointers when passed to `Class *` parameters (MQL5 does); #import, #resource,
    #define-generated declarations spanning macros, operator-precedence warnings, "empty controlled statement",
    "unreachable code", "possible use of uninitialised array element", properties like #property strict/#property version
    validity, input-name length/duplicate limits, string literal > 63 chars in inputs, identifiers that collide with MQL5
    reserved words (the C++-only keywords are renamed instead), the 64K local-variable limits, and tester/runtime
    behaviour (array out of range at run time, zero divide with variables) are NOT checked.
  - Column numbers refer to the translated text and can differ a little from the .mq5; the line number is exact.
  - -Wshadow also reports a local hiding a class member (MetaEditor warns similarly but wording/trigger may differ).
