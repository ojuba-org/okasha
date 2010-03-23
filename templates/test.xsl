<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
        <foo><xsl:value-of select="/a/b/text()" /></foo>
  </xsl:template>
</xsl:stylesheet>
