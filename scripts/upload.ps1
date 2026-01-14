# .\scripts\upload.ps1 -Message "your commit msg" 
param(
  [string]$Message = "update"
)

python .\scripts\copy_mdf.py
git add .
git commit -m "$Message"
git push
