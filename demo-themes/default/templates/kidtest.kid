<?xml version='1.0' encoding='utf-8'?>
<?python
import time
title = "A Kid Template"
?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
>
  <head>
    <title py:content="title">
      This is replaced with the value of the title variable.
    </title>
  </head>
  <body>
  <h1 py:content="h1">title goes here</h1>
    <ul>
    <li py:for="fruit in ls">I like ${fruit}s</li>
    </ul>
    <p>
      The current time is ${time.strftime('%C %c')}.
    </p>
  </body>
</html>

