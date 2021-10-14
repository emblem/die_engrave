import os

names = ["brown_rat", "coyote", "crow", "groundhog", "raccoon", "red_fox", "squirrel", "whitetail"]

for name in names:
    outline = name + "-wrapped.ngc"
    v_clean = name + "_v_clean-wrapped.ngc"
    output = name + "_combined-wrapped.ngc"
    cmd = "cat " + outline + " glue_code.ngc " + v_clean + " > " + output
    os.system(cmd)

print("Done")