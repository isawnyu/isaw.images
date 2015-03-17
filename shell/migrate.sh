#!/bin/bash

#declare -a files=('bags' 'flickr' 'gen' 'masters' 'meta' 'orginals' 'thumbanails' 'exif' 'history' 'hashes')
declare -a checkfiles=('meta')
declare -a files=('flickr' 'masters' 'meta' 'originals' 'thumbnails' 'review-images')
declare -A suffixmap=( ["originals"]="original" ["meta"]="meta" ["flickr"]="flickr" ["masters"]="master" ["thumbnails"]="thumb" ["review-images"]="review")
declare -A extensionmap=( ["originals"]="*" ["meta"]="xml" ["flickr"]="jpg" ["masters"]="tif" ["thumbnails"]="jpg" ["review-images"]="jpg") 
perm="u+rwx"
seed="meta"

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

function createSHA1 {
	srcfile="$1"
	destdir="$2"

	filename="h.txt"
	sha=`sha1sum "$srcfile"`
	echo $sha > "$destdir-jhove-destdirsha1.txt"
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

			mkdir -p "$sitedestdir/$code"
			`chmod "$perm" "$sitedestdir/$code"`
			mkdir -p "$sitedestdir/$code/jhove"
			`chmod "$perm" "$sitedestdir/$code/jhove"`

			for folder in ${files[@]}
			do
				echo "$folder"

				suffix=${suffixmap["$folder"]}
				ext=${extensionmap["$folder"]}
					
				filepatern="$prefix-$code-$suffix.$ext"
				if [[ "$folder" == "originals" ]];
				then
					filepatern="$prefix-$code-$suffix$ext"
				fi

				echo "$filepatern"
				if  [[ "$suffix" == "flickr" ]];
				then 
					suffix="flickr_old"
				elif [[ "$suffix" == "review" ]];
				then
					suffix="preview"
				fi

				dest="$sitedestdir/$code/$suffix.$ext"
				declare -a srcarr=("$srcdir/$folder/$filepatern")
#				src="$srcdir/$folder/$filepatern"

				for src in ${srcarr[@]}
				do
					echo "$src"
					if [ -f "$src" ]
					then	
						echo "source condi"			
						for f in $src
						do
							echo "$f"			
							if [ -f "$f" ] 
							then
								echo "its a file"
								if [[ "$folder" == "originals" ]]
								then
									original_dest="${f##*original}"
									echo "$original_dest"
									dest="$sitedestdir/$code/$suffix$original_dest"
									if [[ "$f" == *"jhove"* ]]; then
										echo "contains";
										dest="$sitedestdir/$code/jhove/$suffix$original_dest"
										createSHA1 "$f" "$sitedestdir/$code/jhove/$suffix"
									fi
#									dest="$sitedestdir/$code/$suffix$original_dest"
								fi
								`cp "$f" "$dest"`
								echo "$dest"
							fi
						done
					fi
				done
			echo "---------------------------------------"
			done				
			histFileName="$sitedestdir/$code/history.txt"
			touch $histFileName || exit
			
			current_time=$(date --utc +%FT%TZ)
			printf '%s\n\t%s\n' $current_time 'Uttara Chavan' >> $histFileName
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

#if [ ! -d "$2" ];
#then
	#echo "parameter 2 not a directory" 1>&2
	##exit 1
#fi

src="$1"
dest="$2"

checksrc "$src"

sitedestdir="dest"`echo "$src" | sed -e 's/^.*\(\/[^/]\)/\1/g'`
startcopy "$src" "$sitedestdir"


