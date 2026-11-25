def test_add_and_list_incident(client):
    response = client.post(
        "/incidents/add",
        data={
            "titre": "Panne réseau",
            "description": "Plus d'accès internet dans la salle.",
            "lieu": "Salle A04",
            "priorite": "Élevée",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Panne réseau" in html
    assert "Salle A04" in html
    assert "Nouveau" in html


def test_add_incident_validation_error(client):
    response = client.post(
        "/incidents/add",
        data={
            "titre": "",
            "description": "Description sans titre",
            "lieu": "Labo 1",
            "priorite": "Moyenne",
        },
    )
    assert response.status_code == 400
    assert "Veuillez remplir tous les champs" in response.get_data(as_text=True)


def test_incident_detail_and_status_update(client):
    client.post(
        "/incidents/add",
        data={
            "titre": "Imprimante bloquée",
            "description": "Bourrage papier récurrent.",
            "lieu": "Secrétariat",
            "priorite": "Faible",
        },
    )

    detail_response = client.get("/incidents/1")
    assert detail_response.status_code == 200
    assert "Imprimante bloquée" in detail_response.get_data(as_text=True)

    status_response = client.post(
        "/incidents/1/status",
        data={"statut": "En cours"},
        follow_redirects=True,
    )
    assert status_response.status_code == 200
    assert "En cours" in status_response.get_data(as_text=True)


def test_delete_incident(client):
    client.post(
        "/incidents/add",
        data={
            "titre": "Écran cassé",
            "description": "L'écran ne s'allume plus.",
            "lieu": "Labo B2",
            "priorite": "Moyenne",
        },
    )

    delete_response = client.post("/incidents/1/delete", follow_redirects=True)
    assert delete_response.status_code == 200
    assert "Écran cassé" not in delete_response.get_data(as_text=True)

    not_found_response = client.get("/incidents/1")
    assert not_found_response.status_code == 404
