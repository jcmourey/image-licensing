# Recursively walk through all arrays and objects, preserving key order.
def walk(f):
  if type == "object" then
    (to_entries | map(.value |= walk(f)) | from_entries) | f
  elif type == "array" then
    map(walk(f)) | f
  else
    f
  end;

# For each object, replace *_id keys with a placeholder in uppercase, preserving order.
walk(
  if type == "object" then
    to_entries
    | map(
        if .key | test("_id$") then
          .value = ("<" + (.key | sub("_id$";"") | ascii_upcase) + "_ID>")
        else
          .
        end
      )
    | from_entries
  else
    .
  end
)
