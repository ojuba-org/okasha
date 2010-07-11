#! /bin/bash
baseurl="http://www.ojuba.org/wiki/_export/xhtml/okasha/"
for i in "" deployment sample1 templates elixir
do
fn="${i:-about}.html"
i="${i:-الصفحة_الأولى}"
echo "getting $fn from ${baseurl}${i}"
rm "$fn" 2>/dev/null || :
curl -L -o "$fn" "${baseurl}${i}"

perl -i -lwne 'BEGIN{$echo=1;}
s:href="/wiki/okasha/([^"]+)":href="${1}.html":g;
s:src="/wiki/_media/okasha/([^?"]+)(\?[^"]*)?":src="../files/$1":g;
s:href="/wiki/_detail/okasha/([^?"]+)(\?[^"]*)?":href="../files/$1":g;
s:okasha-logo:logo:g;
if(/#discussion__section|\<(link|meta|script)[^>]*\>/){next;}if (/class="tags"/) {$echo=0;}
if(/\<\/head\>/) {
 print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />";
 print "<link rel=\"stylesheet\" media=\"all\" type=\"text/css\" href=\"all.css\" />";
 print "<link rel=\"stylesheet\" media=\"screen\" type=\"text/css\" href=\"screen.css\" />";
 print "<link rel=\"stylesheet\" media=\"print\" type=\"text/css\" href=\"print.css\" />";
}
if($echo){print $_;}if (/\<\/div\>/) {$echo=1;}' "$fn"

done

