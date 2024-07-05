%{
#include "regexp.tab.h"
%}

%%
\n[a-z]+ 	    {yylval.str = strdup(yytext); return MOT;}
[a-zEO] 	    {yylval.str = strdup(yytext); return LETTRE;}
"+"		        {return UNION;}
"."		        {return CONCAT;}
"*"		        {return ETOILE;}
"("		        {return PAR_O;}
")"		        {return PAR_F;}
[ \t]		    {;}
\n              {return 0;}
.               {fprintf(stderr, "Erreur de syntaxe ligne %d, caractère inattendu : %s\n", yylineno, yytext); exit(1);}
%%