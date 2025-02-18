# Downloading Crane here so that the EV2 shell has what it needs to push to the ACR, putting it in with script
Invoke-WebRequest -Uri https://github.com/google/go-containerregistry/releases/download/v0.19.1/go-containerregistry_Linux_x86_64.tar.gz -OutFile src/Shell/crane.tar.gz
pushd src/Shell
dir 
tar xzvf crane.tar.gz
popd

# packaging everything together: script and crane
7z a -ttar src/Run.tar ./src/Shell/*

# EV2 doesn't handle non utf8 characters well and the encoding powershell uses
# varies a lot between version to version.  Using this dot net method should produce a utf8 w/o BOM encoding.
$versionContent = $env:BUILD_BUILDNUMBER
$versionFileName = ".\deploy\ev2\buildver.txt"


# If the file already exists, delete it so you can recreate it and repopulate with the build number
if (Test-Path -Path $versionFileName -PathType Leaf) {
  Remove-Item -Path $versionFileName
}

# Create the empty file so we can resolve the path
New-Item -Name $versionFileName -ItemType File

# WriteAllLines requires an absolute path
$versionFile = Convert-Path $versionFileName
[IO.File]::WriteAllText($versionFile, $versionContent)