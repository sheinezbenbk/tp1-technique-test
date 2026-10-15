"""Application Flask du Triangulator."""

from flask import Flask


def create_app(pointset_client) -> Flask:
    """Création de l'application Flask.
    
    `pointset_client`est injecté : en production c'est un vrai 
    PointSetClient, dans les tests c'est un faux client (stub).
    """
    raise NotImplementedError