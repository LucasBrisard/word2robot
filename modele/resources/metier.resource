*** Settings ***
Documentation    Mots-clés métier du projet {{PROJET}} : une intention par mot-clé, avec ses attentes et
...              assertions. Les mots-clés communs (navigateur, ouverture de l'application, personas,
...              capture de fin) viennent de commun/session.resource.

Variables        ../projet.yaml
Resource         ../../../commun/session.resource
Resource         locators.resource
