# mPyPl

## Monadic Pipeline Library for Python

This library was created by a team of enthusiastic software developers / data scientists at Microsoft, who
wanted to simplify tasks of data processing and creating complex data pipelines. The library is inspired
by the following main ideas:

 * Using functional approach to data processing (which implies immutability, lazy evaluation, etc.) 
 * Using [pipe](https://github.com/JulienPalard/Pipe) module in Python to achieve data pipelines similar to 
   [F#](http://fsharp.org).
 * Data pipeline uses dictionaries with different fields as base type, new operations would typically enrich data and add 
   new fields by using `apply` function. Those dictionaries are similar to *monads*, and `apply` is similar to *lift* operation
   on monads. Thus the naming of the library.
   
## Credits

Principal developers of mPyPl:

 * [Dmitri Soshnikov](https://github.com/shwars)
 * [Yana Valieva](https://github.com/vJenny)
 * [Tim Scarfe](https://github.com/ecsplendid)
 