before = "100,000.000"

print(f"before:\n{before}\n")

# get index of decimal dot
dot = before.rindex(".")

if dot == -1:
    print(f"'{before}' is not a valid float!")
    exit(1)

# replace all commas with dots
inbetween = before.replace(",", ".")

print(f"inbetween:\n{inbetween}\n")

# replace decimal dot with comma
after = inbetween[:dot] + "," + inbetween[dot + 1 :]