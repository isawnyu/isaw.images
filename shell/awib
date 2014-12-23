#!/bin/bash

#declare -a files=('bags' 'flickr' 'gen' 'masters' 'meta' 'orginals' 'thumbanails' 'exif' 'history' 'hashes')
declare -a checkfiles=('meta')
declare -a files=('flickr' 'masters' 'meta' 'originals')
declare -A suffixmap=( ["originals"]="original" ["meta"]="meta" ["flickr"]="flickr" ["masters"]="master")
declare -A extensionmap=( ["originals"]="*" ["meta"]="xml" ["flickr"]="jpg" ["masters"]="tif")
perm="u+rwx"
seed="meta"
function createsubfolders {
	
	mkdir -p "$1"
	`chmod "$perm" "$1"`
	for folder in ${files[@]}
	do
		mkdir -p "$1/$folder"
		`chmod "$perm" "$1/$folder"`
	done
}

function checksrc {

	for folder in ${checkfiles[@]}
	do
		if [ ! -d "$1/$folder" ];
		then
			echo "src directory doesn't contain $folder" 1>&2
			#exit 1
		fi
	done
}

function startcopy {
	srcdir="$1"
	sitedestdir="$2"

	seedfolder="$1/$seed/*"
	for file in $seedfolder
	do
		if [ -f "$file" ]
		then
			filename=`echo "$file" | sed -e "s/^.*\/\([^/]\)/\1/g"`
			code=`echo "$filename" | sed -e "s/^isawi\-\([0-9]*\)\-meta\.\(xml\|XML\)/\1/g"`
			prefix="isawi"
			createsubfolders "$sitedestdir/$code"
			for folder in ${files[@]}
			do
				suffix=${suffixmap["$folder"]}
				ext=${extensionmap["$folder"]}
				dest="$sitedestdir/$code/$folder"
				filepatern="$prefix-$code-$suffix.$ext"
				src="$srcdir/$folder/$filepatern"
				if [ -f "$src" ]
				then				
					for f in $src
					do
						if [ -f "$f" ] 
						then
							`cp "$f" "$dest"`
						fi
					done
				fi
			done		
		fi
	done
}

if [[ "$#" = 0 ]]
then
	echo "No option is given" 1>&2
	exit 1
fi

if [ ! -d "$1" ];
then
	echo "parameter 1 not a directory" 1>&2
	#exit 1
fi

if [ ! -d "$2" ];
then
	echo "parameter 2 not a directory" 1>&2
	#exit 1
fi

src="$1"
dest="$2"

checksrc "$src"

sitedestdir="$dest"`echo "$src" | sed -e 's/^.*\(\/[^/]\)/\1/g'`
startcopy "$src" "$sitedestdir"

