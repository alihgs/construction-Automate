%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if YYBISON
int yylex();
int yyerror(const char *s);
int yyparse();
#endif
int compteur = 0;
char* code;

char* generer_operation_deux_arguments(char* operation, int compteur, char* expr1, char* expr2) {
    char* res;
    asprintf(&res, "%s%sa%d = %s(a%d, a%d)\n", expr1, expr2, compteur, operation, compteur-2, compteur-1);
    free(expr1);
    free(expr2);
    return res;
}

char* generer_operation_un_argument(char* operation, int compteur, char* expr) {
    char* res;
    asprintf(&res, "%sa%d = %s(a%d)\n", expr, compteur, operation, compteur-1);
    free(expr);
    return res;
}

char* generer_automate(int compteur, char* lettre) {
    char* res;
    asprintf(&res, "a%d = automate(\"%s\")\n", compteur, lettre);
    return res;
}

void supprimer_saut_de_ligne(char** str) {
    if ((*str)[0] == '\n') {
        memmove(*str, *str + 1, strlen(*str));
    }
}

char* generer_mot(char* mot, char* mots) {
    supprimer_saut_de_ligne(&mot);
    char* res;
    asprintf(&res, "print(reconnait(a_final,\"%s\"))\n%s", mot, mots);
    free(mots);
    return res;
}

char* generer_mot_seul(char* mot) {
    supprimer_saut_de_ligne(&mot);
    char* res;
    asprintf(&res, "print(reconnait(a_final,\"%s\"))", mot);
    return res;
}

char* generer_code(char* expression, char* mots) {
    char* res;
    asprintf(&res, "from automate import *\n\n%s\na_final = a%d\nprint(a_final)\n%s", expression, compteur-1, mots);
    free(expression);
    free(mots);
    return res;
}

int main() {
    FILE *fichier_main_python = fopen("main.py", "w");
    if (fichier_main_python == NULL) {
        fprintf(stderr, "Failed to open fichier_main_python\n");
        return 1;
    }
    yyparse();
    fprintf(fichier_main_python, "%s\n", code);
    fclose(fichier_main_python);
    free(code);
    return 0;
}
%}

%union {
    char* str;
}

%token <str> MOT
%token <str> LETTRE
%token PAR_O
%token PAR_F

%type <str> expression
%type <str> mots

%left UNION
%left CONCAT
%left ETOILE

%%
input:
        expression mots {
            code = generer_code($1, $2);
        }
    ;

expression:
        expression UNION expression {
            $$ = generer_operation_deux_arguments("union", compteur, $1, $3);
            compteur++;
        }
    |   expression CONCAT expression {
            $$ = generer_operation_deux_arguments("concatenation", compteur, $1, $3);
            compteur++;
        }
    |   expression ETOILE {
            $$ = generer_operation_un_argument("etoile", compteur, $1);
            compteur++;
        }
    |   PAR_O expression PAR_F {
            $$ = $2;
        }
    |   LETTRE {
            $$ = generer_automate(compteur, $1);
            compteur++;
    }
    ;

mots:
        MOT mots {
            $$ = generer_mot($1, $2);
        }
    |   MOT {
            $$ = generer_mot_seul($1);
        }
    ;
%%