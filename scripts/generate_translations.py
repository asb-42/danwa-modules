#!/usr/bin/env python3
"""Generate all translation files from English source with fallback.

Generates ui_strings.json for all 55 locales. Translated strings are
provided per locale; missing keys fall back to English values.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
EN_SOURCE = ROOT / "ui-translations/lang-en/ui_strings.json"

# ──────────────────────────────────────────────────────────────────────
# TRANSLATIONS: {locale: {key: translated_value}}
# Only the most important ~300-400 UI strings per language.
# Missing keys automatically fall back to English.
# ──────────────────────────────────────────────────────────────────────

# Common translations shared by Romance languages (fr/es/it/pt/ro)
_ROMANCE = {
    # nav
    "nav.dashboard": {"fr": "Tableau de bord", "es": "Panel de control", "it": "Pannello di controllo", "pt": "Painel de controlo", "ro": "Panou de control"},
    "nav.debate": {"fr": "Débat actif", "es": "Debate activo", "it": "Dibattito attivo", "pt": "Debate ativo", "ro": "Dezbatere activă"},
    "nav.archive": {"fr": "Archives", "es": "Archivo", "it": "Archivio", "pt": "Arquivo", "ro": "Arhivă"},
    "nav.audit": {"fr": "Journal d'audit", "es": "Registro de auditoría", "it": "Registro di controllo", "pt": "Registro de auditoria", "ro": "Jurnal de audit"},
    "nav.config": {"fr": "Configuration", "es": "Configuración", "it": "Configurazione", "pt": "Configuração", "ro": "Configurare"},
    "nav.output": {"fr": "Sortie", "es": "Salida", "it": "Uscita", "pt": "Saída", "ro": "Ieșire"},
    "nav.documents": {"fr": "Documents", "es": "Documentos", "it": "Documenti", "pt": "Documentos", "ro": "Documente"},
    "nav.projects": {"fr": "Projets", "es": "Proyectos", "it": "Progetti", "pt": "Projetos", "ro": "Proiecte"},
    "nav.input": {"fr": "Nouveau débat", "es": "Nuevo debate", "it": "Nuovo dibattito", "pt": "Novo debate", "ro": "Nouă dezbatere"},
    "nav.translation": {"fr": "Traduction", "es": "Traducción", "it": "Traduzione", "pt": "Tradução", "ro": "Traducere"},
    "nav.blueprint": {"fr": "Blueprint", "es": "Blueprint", "it": "Blueprint", "pt": "Blueprint", "ro": "Blueprint"},
    "nav.canvas": {"fr": "Canvas", "es": "Lienzo", "it": "Canvas", "pt": "Canvas", "ro": "Canvas"},
    "nav.blueprints": {"fr": "Blueprints", "es": "Blueprints", "it": "Blueprints", "pt": "Blueprints", "ro": "Blueprints"},
    "nav.workflows": {"fr": "Flux de travail", "es": "Flujos de trabajo", "it": "Flussi di lavoro", "pt": "Fluxos de trabalho", "ro": "Fluxuri de lucru"},
    "nav.llmProfiles": {"fr": "Profils LLM", "es": "Perfiles LLM", "it": "Profili LLM", "pt": "Perfis LLM", "ro": "Profiluri LLM"},
    "nav.serviceLlm": {"fr": "LLM de service", "es": "LLM de servicio", "it": "LLM di servizio", "pt": "LLM de serviço", "ro": "LLM de serviciu"},
    "nav.rolesPersonas": {"fr": "Rôles et personas", "es": "Roles y personas", "it": "Ruoli e personas", "pt": "Papéis e personas", "ro": "Roluri și persona"},
    "nav.modules": {"fr": "Modules", "es": "Módulos", "it": "Moduli", "pt": "Módulos", "ro": "Module"},
    "nav.backup": {"fr": "Sauvegarde", "es": "Copia de seguridad", "it": "Backup", "pt": "Backup", "ro": "Backup"},
    "nav.section.run": {"fr": "Exécuter", "es": "Ejecutar", "it": "Esegui", "pt": "Executar", "ro": "Rulare"},
    "nav.section.build": {"fr": "Construire", "es": "Construir", "it": "Costruisci", "pt": "Construir", "ro": "Construire"},
    "nav.section.system": {"fr": "Système", "es": "Sistema", "it": "Sistema", "pt": "Sistema", "ro": "Sistem"},
    "nav.kitsune": {"fr": "Kitsune", "es": "Kitsune", "it": "Kitsune", "pt": "Kitsune", "ro": "Kitsune"},
    "nav.server": {"fr": "Serveur", "es": "Servidor", "it": "Server", "pt": "Servidor", "ro": "Server"},
    "nav.timeline": {"fr": "Chronologie", "es": "Línea de tiempo", "it": "Cronologia", "pt": "Linha do tempo", "ro": "Cronologie"},
    "nav.proposals": {"fr": "Propositions", "es": "Propuestas", "it": "Proposte", "pt": "Propostas", "ro": "Propuneri"},
    "nav.replay": {"fr": "Rejouer", "es": "Repetición", "it": "Replay", "pt": "Replay", "ro": "Replay"},
    # common
    "common.cancel": {"fr": "Annuler", "es": "Cancelar", "it": "Annulla", "pt": "Cancelar", "ro": "Anulare"},
    "common.close": {"fr": "Fermer", "es": "Cerrar", "it": "Chiudi", "pt": "Fechar", "ro": "Închide"},
    "common.confirm": {"fr": "Confirmer", "es": "Confirmar", "it": "Conferma", "pt": "Confirmar", "ro": "Confirmă"},
    "common.delete": {"fr": "Supprimer", "es": "Eliminar", "it": "Elimina", "pt": "Eliminar", "ro": "Șterge"},
    "common.edit": {"fr": "Modifier", "es": "Editar", "it": "Modifica", "pt": "Editar", "ro": "Editare"},
    "common.error": {"fr": "Erreur", "es": "Error", "it": "Errore", "pt": "Erro", "ro": "Eroare"},
    "common.export": {"fr": "Exporter", "es": "Exportar", "it": "Esporta", "pt": "Exportar", "ro": "Exportă"},
    "common.import": {"fr": "Importer", "es": "Importar", "it": "Importa", "pt": "Importar", "ro": "Importă"},
    "common.loading": {"fr": "Chargement...", "es": "Cargando...", "it": "Caricamento...", "pt": "A carregar...", "ro": "Se încarcă..."},
    "common.new": {"fr": "Nouveau", "es": "Nuevo", "it": "Nuovo", "pt": "Novo", "ro": "Nou"},
    "common.refresh": {"fr": "Actualiser", "es": "Actualizar", "it": "Aggiorna", "pt": "Atualizar", "ro": "Reîmprospătare"},
    "common.save": {"fr": "Sauvegarder", "es": "Guardar", "it": "Salva", "pt": "Guardar", "ro": "Salvează"},
    "common.search": {"fr": "Rechercher", "es": "Buscar", "it": "Cerca", "pt": "Pesquisar", "ro": "Căutare"},
    # auth
    "auth.email": {"fr": "E-mail", "es": "Correo electrónico", "it": "E-mail", "pt": "E-mail", "ro": "E-mail"},
    "auth.password": {"fr": "Mot de passe", "es": "Contraseña", "it": "Password", "pt": "Palavra-passe", "ro": "Parolă"},
    "auth.signIn": {"fr": "Se connecter", "es": "Iniciar sesión", "it": "Accedi", "pt": "Iniciar sessão", "ro": "Conectare"},
    "auth.logout": {"fr": "Déconnexion", "es": "Cerrar sesión", "it": "Disconnetti", "pt": "Terminar sessão", "ro": "Deconectare"},
    "auth.createAccount": {"fr": "Créer un compte", "es": "Crear cuenta", "it": "Crea account", "pt": "Criar conta", "ro": "Creare cont"},
    "auth.displayName": {"fr": "Nom d'affichage", "es": "Nombre para mostrar", "it": "Nome visualizzato", "pt": "Nome de exibição", "ro": "Nume afișat"},
    "auth.confirmPassword": {"fr": "Confirmer le mot de passe", "es": "Confirmar contraseña", "it": "Conferma password", "pt": "Confirmar palavra-passe", "ro": "Confirmă parola"},
    "auth.welcomeBack": {"fr": "Bienvenue sur Danwa", "es": "Bienvenido a Danwa", "it": "Benvenuto su Danwa", "pt": "Bem-vindo ao Danwa", "ro": "Bine ați venit pe Danwa"},
    "auth.sessionExpired": {"fr": "Session expirée", "es": "Sesión expirada", "it": "Sessione scaduta", "pt": "Sessão expirada", "ro": "Sesiune expirată"},
    "auth.loggedInAs": {"fr": "Connecté en tant que {name}", "es": "Conectado como {name}", "it": "Connesso come {name}", "pt": "Conectado como {name}", "ro": "Conectat ca {name}"},
    # debate
    "debate.title": {"fr": "Débat", "es": "Debate", "it": "Dibattito", "pt": "Debate", "ro": "Dezbatere"},
    "debate.topic": {"fr": "Sujet", "es": "Tema", "it": "Argomento", "pt": "Tema", "ro": "Subiect"},
    "debate.start": {"fr": "Démarrer le débat", "es": "Iniciar debate", "it": "Avvia dibattito", "pt": "Iniciar debate", "ro": "Pornește dezbaterea"},
    "debate.stop": {"fr": "Arrêter", "es": "Detener", "it": "Ferma", "pt": "Parar", "ro": "Oprește"},
    "debate.pause": {"fr": "Mettre en pause", "es": "Pausar", "it": "Pausa", "pt": "Pausar", "ro": "Pauză"},
    "debate.resume": {"fr": "Reprendre", "es": "Reanudar", "it": "Riprendi", "pt": "Retomar", "ro": "Reia"},
    "debate.round": {"fr": "Round", "es": "Ronda", "it": "Turno", "pt": "Ronda", "ro": "Rundă"},
    "debate.rounds": {"fr": "Rounds", "es": "Rondas", "it": "Turni", "pt": "Rondas", "ro": "Runde"},
    "debate.agents": {"fr": "Agents", "es": "Agentes", "it": "Agenti", "pt": "Agentes", "ro": "Agenți"},
    "debate.context": {"fr": "Contexte", "es": "Contexto", "it": "Contesto", "pt": "Contexto", "ro": "Context"},
    "debate.output": {"fr": "Sortie", "es": "Salida", "it": "Uscita", "pt": "Saída", "ro": "Ieșire"},
    "debate.create": {"fr": "Créer un débat", "es": "Crear debate", "it": "Crea dibattito", "pt": "Criar debate", "ro": "Creare dezbatere"},
    "debate.delete": {"fr": "Supprimer le débat", "es": "Eliminar debate", "it": "Elimina dibattito", "pt": "Eliminar debate", "ro": "Șterge dezbaterea"},
    "debate.save": {"fr": "Sauvegarder", "es": "Guardar", "it": "Salva", "pt": "Guardar", "ro": "Salvează"},
    "debate.export": {"fr": "Exporter", "es": "Exportar", "it": "Esporta", "pt": "Exportar", "ro": "Exportă"},
    "debate.clone": {"fr": "Cloner le débat", "es": "Clonar debate", "it": "Clona dibattito", "pt": "Clonar debate", "ro": "Clonează dezbaterea"},
    "debate.fork": {"fr": "Bifurquer le débat", "es": "Bifurcar debate", "it": "Dirama dibattito", "pt": "Bifurcar debate", "ro": "Bifurcă dezbaterea"},
    "debate.addAgent": {"fr": "Ajouter un agent", "es": "Agregar agente", "it": "Aggiungi agente", "pt": "Adicionar agente", "ro": "Adaugă agent"},
    "debate.addRound": {"fr": "Ajouter un round", "es": "Agregar ronda", "it": "Aggiungi turno", "pt": "Adicionar ronda", "ro": "Adaugă rundă"},
    "debate.maxRounds": {"fr": "Rounds maximum", "es": "Rondas máximas", "it": "Turni massimi", "pt": "Rondas máximas", "ro": "Runde maxime"},
    "debate.blueprint": {"fr": "Blueprint", "es": "Blueprint", "it": "Blueprint", "pt": "Blueprint", "ro": "Blueprint"},
    "debate.workflow": {"fr": "Flux de travail", "es": "Flujo de trabajo", "it": "Flusso di lavoro", "pt": "Fluxo de trabalho", "ro": "Flux de lucru"},
    "debate.vs": {"fr": "VS", "es": "VS", "it": "VS", "pt": "VS", "ro": "VS"},
    "debate.history": {"fr": "Historique", "es": "Historial", "it": "Cronologia", "pt": "Histórico", "ro": "Istoric"},
    "debate.duration": {"fr": "Durée", "es": "Duración", "it": "Durata", "pt": "Duração", "ro": "Durată"},
    "debate.status": {"fr": "Statut", "es": "Estado", "it": "Stato", "pt": "Estado", "ro": "Stare"},
    "debate.status.active": {"fr": "Actif", "es": "Activo", "it": "Attivo", "pt": "Ativo", "ro": "Activ"},
    "debate.status.completed": {"fr": "Terminé", "es": "Completado", "it": "Completato", "pt": "Concluído", "ro": "Finalizat"},
    "debate.status.draft": {"fr": "Brouillon", "es": "Borrador", "it": "Bozza", "pt": "Rascunho", "ro": "Ciornă"},
    "debate.status.paused": {"fr": "En pause", "es": "En pausa", "it": "In pausa", "pt": "Em pausa", "ro": "În pauză"},
    "debate.status.running": {"fr": "En cours", "es": "En ejecución", "it": "In esecuzione", "pt": "Em execução", "ro": "În execuție"},
    "debate.status.cancelled": {"fr": "Annulé", "es": "Cancelado", "it": "Annullato", "pt": "Cancelado", "ro": "Anulat"},
    # dashboard
    "dashboard.title": {"fr": "Tableau de bord", "es": "Panel de control", "it": "Pannello di controllo", "pt": "Painel de controlo", "ro": "Panou de control"},
    "dashboard.activeDebates": {"fr": "Débats actifs", "es": "Debates activos", "it": "Dibattiti attivi", "pt": "Debates ativos", "ro": "Dezbateri active"},
    "dashboard.totalDebates": {"fr": "Total des débats", "es": "Total de debates", "it": "Totale dibattiti", "pt": "Total de debates", "ro": "Total dezbateri"},
    "dashboard.quickStart": {"fr": "Démarrage rapide", "es": "Inicio rápido", "it": "Avvio rapido", "pt": "Início rápido", "ro": "Pornire rapidă"},
    # config
    "config.language": {"fr": "Langue", "es": "Idioma", "it": "Lingua", "pt": "Idioma", "ro": "Limbă"},
    "config.darkMode": {"fr": "Mode sombre", "es": "Modo oscuro", "it": "Modalità scura", "pt": "Modo escuro", "ro": "Mod întunecat"},
    "config.save": {"fr": "Sauvegarder", "es": "Guardar", "it": "Salva", "pt": "Guardar", "ro": "Salvează"},
    "config.reset": {"fr": "Réinitialiser", "es": "Restablecer", "it": "Ripristina", "pt": "Repor", "ro": "Resetare"},
    "config.temperature": {"fr": "Température", "es": "Temperatura", "it": "Temperatura", "pt": "Temperatura", "ro": "Temperatură"},
    "config.model": {"fr": "Modèle", "es": "Modelo", "it": "Modello", "pt": "Modelo", "ro": "Model"},
    "config.provider": {"fr": "Fournisseur", "es": "Proveedor", "it": "Fornitore", "pt": "Fornecedor", "ro": "Furnizor"},
    "config.apiKey": {"fr": "Clé API", "es": "Clave API", "it": "Chiave API", "pt": "Chave API", "ro": "Cheie API"},
    "config.timeout": {"fr": "Délai d'expiration", "es": "Tiempo de espera", "it": "Timeout", "pt": "Tempo limite", "ro": "Timeout"},
    "config.general": {"fr": "Général", "es": "General", "it": "Generale", "pt": "Geral", "ro": "General"},
    "config.export": {"fr": "Exporter", "es": "Exportar", "it": "Esporta", "pt": "Exportar", "ro": "Exportă"},
    "config.import": {"fr": "Importer", "es": "Importar", "it": "Importa", "pt": "Importar", "ro": "Importă"},
    # archive
    "archive.title": {"fr": "Archives", "es": "Archivo", "it": "Archivio", "pt": "Arquivo", "ro": "Arhivă"},
    "archive.search": {"fr": "Rechercher dans les archives", "es": "Buscar en archivos", "it": "Cerca nell'archivio", "pt": "Pesquisar no arquivo", "ro": "Căutare în arhivă"},
    "archive.export": {"fr": "Exporter", "es": "Exportar", "it": "Esporta", "pt": "Exportar", "ro": "Exportă"},
    "archive.empty": {"fr": "Aucun débat archivé", "es": "No hay debates archivados", "it": "Nessun dibattito archiviato", "pt": "Nenhum debate arquivado", "ro": "Nicio dezbatere arhivată"},
    # modules
    "modules.title": {"fr": "Modules", "es": "Módulos", "it": "Moduli", "pt": "Módulos", "ro": "Module"},
    "modules.install": {"fr": "Installer", "es": "Instalar", "it": "Installa", "pt": "Instalar", "ro": "Instalare"},
    "modules.uninstall": {"fr": "Désinstaller", "es": "Desinstalar", "it": "Disinstalla", "pt": "Desinstalar", "ro": "Dezinstalare"},
    "modules.update": {"fr": "Mettre à jour", "es": "Actualizar", "it": "Aggiorna", "pt": "Atualizar", "ro": "Actualizare"},
    "modules.search": {"fr": "Rechercher des modules", "es": "Buscar módulos", "it": "Cerca moduli", "pt": "Pesquisar módulos", "ro": "Căutare module"},
    "modules.active": {"fr": "Actifs", "es": "Activos", "it": "Attivi", "pt": "Ativos", "ro": "Active"},
    "modules.available": {"fr": "Disponibles", "es": "Disponibles", "it": "Disponibili", "pt": "Disponíveis", "ro": "Disponibile"},
    # documents
    "documents.title": {"fr": "Documents", "es": "Documentos", "it": "Documenti", "pt": "Documentos", "ro": "Documente"},
    "documents.upload": {"fr": "Téléverser", "es": "Subir", "it": "Carica", "pt": "Carregar", "ro": "Încărcare"},
    "documents.delete": {"fr": "Supprimer", "es": "Eliminar", "it": "Elimina", "pt": "Eliminar", "ro": "Șterge"},
    "documents.search": {"fr": "Rechercher des documents", "es": "Buscar documentos", "it": "Cerca documenti", "pt": "Pesquisar documentos", "ro": "Căutare documente"},
    # projects
    "projects.title": {"fr": "Projets", "es": "Proyectos", "it": "Progetti", "pt": "Projetos", "ro": "Proiecte"},
    "projects.create": {"fr": "Créer un projet", "es": "Crear proyecto", "it": "Crea progetto", "pt": "Criar projeto", "ro": "Creare proiect"},
    "projects.delete": {"fr": "Supprimer le projet", "es": "Eliminar proyecto", "it": "Elimina progetto", "pt": "Eliminar projeto", "ro": "Șterge proiectul"},
    # backup
    "backup.title": {"fr": "Sauvegarde", "es": "Copia de seguridad", "it": "Backup", "pt": "Backup", "ro": "Backup"},
    "backup.create": {"fr": "Créer une sauvegarde", "es": "Crear copia de seguridad", "it": "Crea backup", "pt": "Criar backup", "ro": "Creare backup"},
    "backup.restore": {"fr": "Restaurer", "es": "Restaurar", "it": "Ripristina", "pt": "Restaurar", "ro": "Restaurare"},
    # workflow
    "workflow.title": {"fr": "Flux de travail", "es": "Flujos de trabajo", "it": "Flussi di lavoro", "pt": "Fluxos de trabalho", "ro": "Fluxuri de lucru"},
    "workflow.create": {"fr": "Créer un flux de travail", "es": "Crear flujo de trabajo", "it": "Crea flusso di lavoro", "pt": "Criar fluxo de trabalho", "ro": "Creare flux de lucru"},
    "workflow.run": {"fr": "Exécuter", "es": "Ejecutar", "it": "Esegui", "pt": "Executar", "ro": "Rulează"},
    # app
    "app.name": {"fr": "Danwa", "es": "Danwa", "it": "Danwa", "pt": "Danwa", "ro": "Danwa"},
    "app.tagline": {"fr": "Moteur de débat multi-agents", "es": "Motor de debate multi-agente", "it": "Motore di dibattito multi-agente", "pt": "Motor de debate multi-agente", "ro": "Motor de dezbatere multi-agent"},
    # toast
    "toast.success": {"fr": "Opération réussie", "es": "Operación exitosa", "it": "Operazione riuscita", "pt": "Operação bem-sucedida", "ro": "Operațiune reușită"},
    "toast.error": {"fr": "Une erreur s'est produite", "es": "Ocurrió un error", "it": "Si è verificato un errore", "pt": "Ocorreu um erro", "ro": "A apărut o eroare"},
    # error
    "error.generic": {"fr": "Une erreur s'est produite", "es": "Ocurrió un error", "it": "Si è verificato un errore", "pt": "Ocorreu um erro", "ro": "A apărut o eroare"},
    "error.network": {"fr": "Erreur réseau", "es": "Error de red", "it": "Errore di rete", "pt": "Erro de rede", "ro": "Eroare de rețea"},
    "error.notFound": {"fr": "Non trouvé", "es": "No encontrado", "it": "Non trovato", "pt": "Não encontrado", "ro": "Negăsit"},
    "error.unauthorized": {"fr": "Non autorisé", "es": "No autorizado", "it": "Non autorizzato", "pt": "Não autorizado", "ro": "Neautorizat"},
    # translation
    "translation.title": {"fr": "Traduction", "es": "Traducción", "it": "Traduzione", "pt": "Tradução", "ro": "Traducere"},
    "translation.language": {"fr": "Langue", "es": "Idioma", "it": "Lingua", "pt": "Idioma", "ro": "Limbă"},
    "translation.save": {"fr": "Sauvegarder", "es": "Guardar", "it": "Salva", "pt": "Guardar", "ro": "Salvează"},
    # settings
    "settings.title": {"fr": "Paramètres", "es": "Configuración", "it": "Impostazioni", "pt": "Definições", "ro": "Setări"},
    "settings.general": {"fr": "Général", "es": "General", "it": "Generale", "pt": "Geral", "ro": "General"},
    "settings.language": {"fr": "Langue", "es": "Idioma", "it": "Lingua", "pt": "Idioma", "ro": "Limbă"},
    "settings.save": {"fr": "Sauvegarder", "es": "Guardar", "it": "Salva", "pt": "Guardar", "ro": "Salvează"},
    # profile
    "profile.title": {"fr": "Profil", "es": "Perfil", "it": "Profilo", "pt": "Perfil", "ro": "Profil"},
    "profile.save": {"fr": "Sauvegarder", "es": "Guardar", "it": "Salva", "pt": "Guardar", "ro": "Salvează"},
    # users
    "users.title": {"fr": "Utilisateurs", "es": "Usuarios", "it": "Utenti", "pt": "Utilizadores", "ro": "Utilizatori"},
    "users.addUser": {"fr": "Ajouter un utilisateur", "es": "Agregar usuario", "it": "Aggiungi utente", "pt": "Adicionar utilizador", "ro": "Adaugă utilizator"},
    # search
    "search.placeholder": {"fr": "Rechercher...", "es": "Buscar...", "it": "Cerca...", "pt": "Pesquisar...", "ro": "Căutare..."},
    "search.noResults": {"fr": "Aucun résultat", "es": "Sin resultados", "it": "Nessun risultato", "pt": "Sem resultados", "ro": "Fără rezultate"},
}

# Germanic languages (nl, da, sv, nb, nn)
_GERMANIC = {
    "nav.dashboard": {"nl": "Dashboard", "da": "Dashboard", "sv": "Instrumentpanel", "nb": "Dashbord", "nn": "Dashbord"},
    "nav.debate": {"nl": "Actief debat", "da": "Aktiv debat", "sv": "Aktiv debatt", "nb": "Aktiv debatt", "nn": "Aktiv debatt"},
    "nav.archive": {"nl": "Archief", "da": "Arkiv", "sv": "Arkiv", "nb": "Arkiv", "nn": "Arkiv"},
    "nav.config": {"nl": "Configuratie", "da": "Konfiguration", "sv": "Konfiguration", "nb": "Konfigurasjon", "nn": "Konfigurasjon"},
    "nav.output": {"nl": "Uitvoer", "da": "Output", "sv": "Utdata", "nb": "Utdata", "nn": "Utdata"},
    "nav.documents": {"nl": "Documenten", "da": "Dokumenter", "sv": "Dokument", "nb": "Dokumenter", "nn": "Dokument"},
    "nav.projects": {"nl": "Projecten", "da": "Projekter", "sv": "Projekt", "nb": "Prosjekter", "nn": "Prosjekt"},
    "nav.modules": {"nl": "Modules", "da": "Moduler", "sv": "Moduler", "nb": "Moduler", "nn": "Modular"},
    "nav.backup": {"nl": "Back-up", "da": "Sikkerhedskopi", "sv": "Säkerhetskopia", "nb": "Sikkerhetskopi", "nn": "Sikkerheitskopi"},
    "nav.workflows": {"nl": "Workflows", "da": "Arbejdsgange", "sv": "Arbetsflöden", "nb": "Arbeidsflyter", "nn": "Arbeidsflyter"},
    "common.cancel": {"nl": "Annuleren", "da": "Annuller", "sv": "Avbryt", "nb": "Avbryt", "nn": "Avbryt"},
    "common.close": {"nl": "Sluiten", "da": "Luk", "sv": "Stäng", "nb": "Lukk", "nn": "Lukk"},
    "common.confirm": {"nl": "Bevestigen", "da": "Bekræft", "sv": "Bekräfta", "nb": "Bekreft", "nn": "Stadfest"},
    "common.delete": {"nl": "Verwijderen", "da": "Slet", "sv": "Ta bort", "nb": "Slett", "nn": "Slett"},
    "common.edit": {"nl": "Bewerken", "da": "Rediger", "sv": "Redigera", "nb": "Rediger", "nn": "Rediger"},
    "common.error": {"nl": "Fout", "da": "Fejl", "sv": "Fel", "nb": "Feil", "nn": "Feil"},
    "common.export": {"nl": "Exporteren", "da": "Eksporter", "sv": "Exportera", "nb": "Eksporter", "nn": "Eksporter"},
    "common.import": {"nl": "Importeren", "da": "Importer", "sv": "Importera", "nb": "Importer", "nn": "Importer"},
    "common.loading": {"nl": "Laden...", "da": "Indlæser...", "sv": "Laddar...", "nb": "Laster...", "nn": "Lastar..."},
    "common.save": {"nl": "Opslaan", "da": "Gem", "sv": "Spara", "nb": "Lagre", "nn": "Lagre"},
    "common.search": {"nl": "Zoeken", "da": "Søg", "sv": "Sök", "nb": "Søk", "nn": "Søk"},
    "debate.title": {"nl": "Debat", "da": "Debat", "sv": "Debatt", "nb": "Debatt", "nn": "Debatt"},
    "debate.start": {"nl": "Start debat", "da": "Start debat", "sv": "Starta debatt", "nb": "Start debatt", "nn": "Start debatt"},
    "debate.stop": {"nl": "Stoppen", "da": "Stop", "sv": "Stoppa", "nb": "Stopp", "nn": "Stopp"},
    "debate.pause": {"nl": "Pauzeren", "da": "Pause", "sv": "Pausa", "nb": "Pause", "nn": "Pause"},
    "debate.round": {"nl": "Ronde", "da": "Runde", "sv": "Runda", "nb": "Runde", "nn": "Runde"},
    "debate.agents": {"nl": "Agenten", "da": "Agenter", "sv": "Agenter", "nb": "Agenter", "nn": "Agentar"},
    "debate.save": {"nl": "Opslaan", "da": "Gem", "sv": "Spara", "nb": "Lagre", "nn": "Lagre"},
    "config.language": {"nl": "Taal", "da": "Sprog", "sv": "Språk", "nb": "Språk", "nn": "Språk"},
    "config.save": {"nl": "Opslaan", "da": "Gem", "sv": "Spara", "nb": "Lagre", "nn": "Lagre"},
    "auth.signIn": {"nl": "Inloggen", "da": "Log ind", "sv": "Logga in", "nb": "Logg inn", "nn": "Logg inn"},
    "auth.logout": {"nl": "Uitloggen", "da": "Log ud", "sv": "Logga ut", "nb": "Logg ut", "nn": "Logg ut"},
    "auth.password": {"nl": "Wachtwoord", "da": "Adgangskode", "sv": "Lösenord", "nb": "Passord", "nn": "Passord"},
    "auth.email": {"nl": "E-mail", "da": "E-mail", "sv": "E-post", "nb": "E-post", "nn": "E-post"},
    "archive.title": {"nl": "Archief", "da": "Arkiv", "sv": "Arkiv", "nb": "Arkiv", "nn": "Arkiv"},
    "modules.title": {"nl": "Modules", "da": "Moduler", "sv": "Moduler", "nb": "Moduler", "nn": "Modular"},
    "documents.title": {"nl": "Documenten", "da": "Dokumenter", "sv": "Dokument", "nb": "Dokumenter", "nn": "Dokument"},
    "projects.title": {"nl": "Projecten", "da": "Projekter", "sv": "Projekt", "nb": "Prosjekter", "nn": "Prosjekt"},
    "workflow.title": {"nl": "Workflows", "da": "Arbejdsgange", "sv": "Arbetsflöden", "nb": "Arbeidsflyter", "nn": "Arbeidsflyter"},
    "settings.title": {"nl": "Instellingen", "da": "Indstillinger", "sv": "Inställningar", "nb": "Innstillinger", "nn": "Innstillingar"},
    "profile.title": {"nl": "Profiel", "da": "Profil", "sv": "Profil", "nb": "Profil", "nn": "Profil"},
    "users.title": {"nl": "Gebruikers", "da": "Brugere", "sv": "Användare", "nb": "Brukere", "nn": "Brukarar"},
    "backup.title": {"nl": "Back-up", "da": "Sikkerhedskopi", "sv": "Säkerhetskopia", "nb": "Sikkerhetskopi", "nn": "Sikkerheitskopi"},
    "error.generic": {"nl": "Er is een fout opgetreden", "da": "Der opstod en fejl", "sv": "Ett fel inträffade", "nb": "En feil oppstod", "nn": "Ein feil oppstod"},
    "toast.success": {"nl": "Succes", "da": "Succes", "sv": "Framgång", "nb": "Suksess", "nn": "Suksess"},
    "app.name": {"nl": "Danwa", "da": "Danwa", "sv": "Danwa", "nb": "Danwa", "nn": "Danwa"},
}

# Slavic languages (pl, sk, hr, sl, sr, cs)
_SLAVIC = {
    "nav.dashboard": {"pl": "Panel główny", "sk": "Ovládací panel", "hr": "Nadzorna ploča", "sl": "Nadzorna plošča", "sr": "Контролна табла", "cs": "Ovládací panel"},
    "nav.debate": {"pl": "Aktywna debata", "sk": "Aktívna debata", "hr": "Aktivna debata", "sl": "Aktivna debata", "sr": "Активна дебата", "cs": "Aktivní debata"},
    "nav.archive": {"pl": "Archiwum", "sk": "Archív", "hr": "Arhiva", "sl": "Arhiv", "sr": "Архива", "cs": "Archiv"},
    "nav.config": {"pl": "Konfiguracja", "sk": "Konfigurácia", "hr": "Konfiguracija", "sl": "Konfiguracija", "sr": "Конфигурација", "cs": "Konfigurace"},
    "nav.documents": {"pl": "Dokumenty", "sk": "Dokumenty", "hr": "Dokumenti", "sl": "Dokumenti", "sr": "Документи", "cs": "Dokumenty"},
    "nav.projects": {"pl": "Projekty", "sk": "Projekty", "hr": "Projekti", "sl": "Projekti", "sr": "Пројекти", "cs": "Projekty"},
    "nav.modules": {"pl": "Moduły", "sk": "Moduly", "hr": "Moduli", "sl": "Moduli", "sr": "Модули", "cs": "Moduly"},
    "nav.backup": {"pl": "Kopia zapasowa", "sk": "Záloha", "hr": "Sigurnosna kopija", "sl": "Varnostna kopija", "sr": "Резервна копија", "cs": "Záloha"},
    "common.cancel": {"pl": "Anuluj", "sk": "Zrušiť", "hr": "Odustani", "sl": "Prekliči", "sr": "Откажи", "cs": "Zrušit"},
    "common.close": {"pl": "Zamknij", "sk": "Zavrieť", "hr": "Zatvori", "sl": "Zapri", "sr": "Затвори", "cs": "Zavřít"},
    "common.confirm": {"pl": "Potwierdź", "sk": "Potvrdiť", "hr": "Potvrdi", "sl": "Potrdi", "sr": "Потврди", "cs": "Potvrdit"},
    "common.delete": {"pl": "Usuń", "sk": "Vymazať", "hr": "Obriši", "sl": "Izbriši", "sr": "Обриши", "cs": "Smazat"},
    "common.edit": {"pl": "Edytuj", "sk": "Upraviť", "hr": "Uredi", "sl": "Uredi", "sr": "Уреди", "cs": "Upravit"},
    "common.error": {"pl": "Błąd", "sk": "Chyba", "hr": "Greška", "sl": "Napaka", "sr": "Грешка", "cs": "Chyba"},
    "common.save": {"pl": "Zapisz", "sk": "Uložiť", "hr": "Spremi", "sl": "Shrani", "sr": "Сачувај", "cs": "Uložit"},
    "common.search": {"pl": "Szukaj", "sk": "Hľadať", "hr": "Pretraži", "sl": "Iskanje", "sr": "Претрага", "cs": "Hledat"},
    "common.loading": {"pl": "Ładowanie...", "sk": "Načítavanie...", "hr": "Učitavanje...", "sl": "Nalaganje...", "sr": "Учитавање...", "cs": "Načítání..."},
    "debate.title": {"pl": "Debata", "sk": "Debata", "hr": "Debata", "sl": "Debata", "sr": "Дебата", "cs": "Debata"},
    "debate.start": {"pl": "Rozpocznij debatę", "sk": "Spustiť debatu", "hr": "Pokreni debatu", "sl": "Začni debato", "sr": "Покрени дебату", "cs": "Spustit debatu"},
    "debate.stop": {"pl": "Zatrzymaj", "sk": "Zastaviť", "hr": "Zaustavi", "sl": "Ustavi", "sr": "Заустави", "cs": "Zastavit"},
    "debate.round": {"pl": "Runda", "sk": "Kolo", "hr": "Runda", "sl": "Runda", "sr": "Рунда", "cs": "Kolo"},
    "debate.save": {"pl": "Zapisz", "sk": "Uložiť", "hr": "Spremi", "sl": "Shrani", "sr": "Сачувај", "cs": "Uložit"},
    "config.language": {"pl": "Język", "sk": "Jazyk", "hr": "Jezik", "sl": "Jezik", "sr": "Језик", "cs": "Jazyk"},
    "config.save": {"pl": "Zapisz", "sk": "Uložiť", "hr": "Spremi", "sl": "Shrani", "sr": "Сачувај", "cs": "Uložit"},
    "auth.signIn": {"pl": "Zaloguj się", "sk": "Prihlásiť sa", "hr": "Prijava", "sl": "Prijava", "sr": "Пријава", "cs": "Přihlásit se"},
    "auth.logout": {"pl": "Wyloguj się", "sk": "Odhlásiť sa", "hr": "Odjava", "sl": "Odjava", "sr": "Одјава", "cs": "Odhlásit se"},
    "auth.password": {"pl": "Hasło", "sk": "Heslo", "hr": "Lozinka", "sl": "Geslo", "sr": "Лозинка", "cs": "Heslo"},
    "archive.title": {"pl": "Archiwum", "sk": "Archív", "hr": "Arhiva", "sl": "Arhiv", "sr": "Архива", "cs": "Archiv"},
    "modules.title": {"pl": "Moduły", "sk": "Moduly", "hr": "Moduli", "sl": "Moduli", "sr": "Модули", "cs": "Moduly"},
    "error.generic": {"pl": "Wystąpił błąd", "sk": "Vyskytla sa chyba", "hr": "Došlo je do greške", "sl": "Prišlo je do napake", "sr": "Дошло је до грешке", "cs": "Došlo k chybě"},
    "app.name": {"pl": "Danwa", "sk": "Danwa", "hr": "Danwa", "sl": "Danwa", "sr": "Danwa", "cs": "Danwa"},
}

# CJK languages (zh, ja, ko)
_CJK = {
    "nav.dashboard": {"zh": "仪表盘", "ja": "ダッシュボード", "ko": "대시보드"},
    "nav.debate": {"zh": "活跃辩论", "ja": "アクティブな討論", "ko": "활성 토론"},
    "nav.archive": {"zh": "归档", "ja": "アーカイブ", "ko": "아카이브"},
    "nav.config": {"zh": "配置", "ja": "設定", "ko": "구성"},
    "nav.output": {"zh": "输出", "ja": "出力", "ko": "출력"},
    "nav.documents": {"zh": "文档", "ja": "ドキュメント", "ko": "문서"},
    "nav.projects": {"zh": "项目", "ja": "プロジェクト", "ko": "프로젝트"},
    "nav.modules": {"zh": "模块", "ja": "モジュール", "ko": "모듈"},
    "nav.backup": {"zh": "备份", "ja": "バックアップ", "ko": "백업"},
    "nav.workflows": {"zh": "工作流", "ja": "ワークフロー", "ko": "워크플로우"},
    "common.cancel": {"zh": "取消", "ja": "キャンセル", "ko": "취소"},
    "common.close": {"zh": "关闭", "ja": "閉じる", "ko": "닫기"},
    "common.confirm": {"zh": "确认", "ja": "確認", "ko": "확인"},
    "common.delete": {"zh": "删除", "ja": "削除", "ko": "삭제"},
    "common.edit": {"zh": "编辑", "ja": "編集", "ko": "편집"},
    "common.error": {"zh": "错误", "ja": "エラー", "ko": "오류"},
    "common.save": {"zh": "保存", "ja": "保存", "ko": "저장"},
    "common.search": {"zh": "搜索", "ja": "検索", "ko": "검색"},
    "common.loading": {"zh": "加载中...", "ja": "読み込み中...", "ko": "로딩 중..."},
    "debate.title": {"zh": "辩论", "ja": "討論", "ko": "토론"},
    "debate.start": {"zh": "开始辩论", "ja": "討論を開始", "ko": "토론 시작"},
    "debate.stop": {"zh": "停止", "ja": "停止", "ko": "중지"},
    "debate.pause": {"zh": "暂停", "ja": "一時停止", "ko": "일시정지"},
    "debate.round": {"zh": "回合", "ja": "ラウンド", "ko": "라운드"},
    "debate.agents": {"zh": "代理", "ja": "エージェント", "ko": "에이전트"},
    "debate.save": {"zh": "保存", "ja": "保存", "ko": "저장"},
    "debate.context": {"zh": "上下文", "ja": "コンテキスト", "ko": "컨텍스트"},
    "debate.output": {"zh": "输出", "ja": "出力", "ko": "출력"},
    "config.language": {"zh": "语言", "ja": "言語", "ko": "언어"},
    "config.save": {"zh": "保存", "ja": "保存", "ko": "저장"},
    "config.darkMode": {"zh": "深色模式", "ja": "ダークモード", "ko": "다크 모드"},
    "config.temperature": {"zh": "温度", "ja": "温度", "ko": "온도"},
    "config.model": {"zh": "模型", "ja": "モデル", "ko": "모델"},
    "config.provider": {"zh": "提供商", "ja": "プロバイダー", "ko": "공급자"},
    "config.apiKey": {"zh": "API 密钥", "ja": "APIキー", "ko": "API 키"},
    "config.timeout": {"zh": "超时", "ja": "タイムアウト", "ko": "타임아웃"},
    "config.general": {"zh": "通用", "ja": "一般", "ko": "일반"},
    "auth.signIn": {"zh": "登录", "ja": "ログイン", "ko": "로그인"},
    "auth.logout": {"zh": "退出", "ja": "ログアウト", "ko": "로그아웃"},
    "auth.password": {"zh": "密码", "ja": "パスワード", "ko": "비밀번호"},
    "auth.email": {"zh": "电子邮件", "ja": "メール", "ko": "이메일"},
    "auth.createAccount": {"zh": "创建账户", "ja": "アカウント作成", "ko": "계정 만들기"},
    "auth.welcomeBack": {"zh": "欢迎回到 Danwa", "ja": "Danwaへようこそ", "ko": "Danwa에 오신 것을 환영합니다"},
    "archive.title": {"zh": "归档", "ja": "アーカイブ", "ko": "아카이브"},
    "modules.title": {"zh": "模块", "ja": "モジュール", "ko": "모듈"},
    "documents.title": {"zh": "文档", "ja": "ドキュメント", "ko": "문서"},
    "projects.title": {"zh": "项目", "ja": "プロジェクト", "ko": "프로젝트"},
    "workflow.title": {"zh": "工作流", "ja": "ワークフロー", "ko": "워크플로우"},
    "settings.title": {"zh": "设置", "ja": "設定", "ko": "설정"},
    "profile.title": {"zh": "个人资料", "ja": "プロフィール", "ko": "프로필"},
    "users.title": {"zh": "用户", "ja": "ユーザー", "ko": "사용자"},
    "backup.title": {"zh": "备份", "ja": "バックアップ", "ko": "백업"},
    "error.generic": {"zh": "发生错误", "ja": "エラーが発生しました", "ko": "오류가 발생했습니다"},
    "error.network": {"zh": "网络错误", "ja": "ネットワークエラー", "ko": "네트워크 오류"},
    "toast.success": {"zh": "操作成功", "ja": "操作が成功しました", "ko": "작업 성공"},
    "translation.title": {"zh": "翻译", "ja": "翻訳", "ko": "번역"},
    "app.name": {"zh": "Danwa", "ja": "Danwa", "ko": "Danwa"},
}

# Other languages
_OTHER = {
    "nav.dashboard": {"tr": "Kontrol paneli", "id": "Dasbor", "ms": "Papan pemuka", "vi": "Bảng điều khiển", "th": "แดชบอร์ด", "tl": "Dashboard", "hu": "Vezérlőpult", "ro": "Panou de control", "bg": "Табло за управление", "mk": "Контролна табла", "ar": "لوحة التحكم", "fa": "داشبورد", "he": "לוח בקרה", "ur": "ڈیش بورڈ", "hi": "डैशबोर्ड", "bn": "ড্যাশবোর্ড", "ta": "டாஷ்போர்டு", "te": "డాష్బోర్డ్", "mr": "डॅशबोर्ड", "sa": "नियन्त्रणपटम्"},
    "common.cancel": {"tr": "İptal", "id": "Batal", "ms": "Batal", "vi": "Hủy", "th": "ยกเลิก", "tl": "Kanselahin", "hu": "Mégsem", "bg": "Отказ", "mk": "Откажи", "ar": "إلغاء", "fa": "لغو", "he": "ביטול", "ur": "منسوخ", "hi": "रद्द करें", "bn": "বাতিল", "ta": "ரத்துசெய்", "te": "రద్దు", "mr": "रद्द करा"},
    "common.delete": {"tr": "Sil", "id": "Hapus", "ms": "Padam", "vi": "Xóa", "th": "ลบ", "tl": "Tanggalin", "hu": "Törlés", "bg": "Изтриване", "mk": "Избриши", "ar": "حذف", "fa": "حذف", "he": "מחק", "ur": "حذف", "hi": "हटाएं", "bn": "মুছুন", "ta": "நீக்கு", "te": "తొలగించు", "mr": "हटवा"},
    "common.save": {"tr": "Kaydet", "id": "Simpan", "ms": "Simpan", "vi": "Lưu", "th": "บันทึก", "tl": "I-save", "hu": "Mentés", "bg": "Запазване", "mk": "Зачувај", "ar": "حفظ", "fa": "ذخیره", "he": "שמור", "ur": "محفوظ", "hi": "सहेजें", "bn": "সংরক্ষণ", "ta": "சேமி", "te": "సేవ్", "mr": "जतन"},
    "common.search": {"tr": "Ara", "id": "Cari", "ms": "Cari", "vi": "Tìm kiếm", "th": "ค้นหา", "tl": "Maghanap", "hu": "Keresés", "bg": "Търсене", "mk": "Пребарување", "ar": "بحث", "fa": "جستجو", "he": "חיפוש", "ur": "تلاش", "hi": "खोजें", "bn": "অনুসন্ধান", "ta": "தேடு", "te": "వెతకండి", "mr": "शोधा"},
    "common.loading": {"tr": "Yükleniyor...", "id": "Memuat...", "ms": "Memuatkan...", "vi": "Đang tải...", "th": "กำลังโหลด...", "tl": "Naglo-load...", "hu": "Betöltés...", "bg": "Зареждане...", "mk": "Се вчитува...", "ar": "جاري التحميل...", "fa": "در حال بارگذاری...", "he": "טוען...", "ur": "لوڈ ہو رہا ہے...", "hi": "लोड हो रहा है...", "bn": "লোড হচ্ছে...", "ta": "ஏற்றுகிறது...", "te": "లోడ్ అవుతోంది...", "mr": "लोड होत आहे..."},
    "debate.title": {"tr": "Tartışma", "id": "Debat", "ms": "Debat", "vi": "Cuộc tranh luận", "th": "การอภิปราย", "tl": "Dibate", "hu": "Vita", "bg": "Дебат", "mk": "Дебата", "ar": "مناقشة", "fa": "مناظره", "he": "ויכוח", "ur": "بحث", "hi": "बहस", "bn": "বিতর্ক", "ta": "விவாதம்", "te": "చర్చ", "mr": "वादविवाद"},
    "debate.start": {"tr": "Tartışmayı başlat", "id": "Mulai debat", "ms": "Mula debat", "vi": "Bắt đầu tranh luận", "th": "เริ่มการอภิปราย", "tl": "Simulan ang dibate", "hu": "Vita indítása", "bg": "Стартиране на дебат", "mk": "Започни дебата", "ar": "بدء المناقشة", "fa": "شروع مناظره", "he": "התחל ויכוח", "ur": "بحث شروع کریں", "hi": "बहस शुरू करें", "bn": "বিতর্ক শুরু", "ta": "விவாதத்தைத் தொடங்கு", "te": "చర్చ ప్రారంభించు", "mr": "वादविवाद सुरू"},
    "config.language": {"tr": "Dil", "id": "Bahasa", "ms": "Bahasa", "vi": "Ngôn ngữ", "th": "ภาษา", "tl": "Wika", "hu": "Nyelv", "bg": "Език", "mk": "Јазик", "ar": "اللغة", "fa": "زبان", "he": "שפה", "ur": "زبان", "hi": "भाषा", "bn": "ভাষা", "ta": "மொழி", "te": "భాష", "mr": "भाषा"},
    "auth.signIn": {"tr": "Giriş yap", "id": "Masuk", "ms": "Log masuk", "vi": "Đăng nhập", "th": "เข้าสู่ระบบ", "tl": "Mag-sign in", "hu": "Bejelentkezés", "bg": "Вход", "mk": "Најава", "ar": "تسجيل الدخول", "fa": "ورود", "he": "התחבר", "ur": "سائن ان", "hi": "साइन इन", "bn": "সাইন ইন", "ta": "உள்நுழை", "te": "సైన్ ఇన్", "mr": "साइन इन"},
    "auth.logout": {"tr": "Çıkış", "id": "Keluar", "ms": "Log keluar", "vi": "Đăng xuất", "th": "ออกจากระบบ", "tl": "Mag-logout", "hu": "Kijelentkezés", "bg": "Излизане", "mk": "Одјава", "ar": "تسجيل الخروج", "fa": "خروج", "he": "התנתק", "ur": "لاگ آؤٹ", "hi": "लॉग आउट", "bn": "লগ আউট", "ta": "வெளியேறு", "te": "లాగ్ అవుట్", "mr": "लॉग आउट"},
    "auth.password": {"tr": "Şifre", "id": "Kata sandi", "ms": "Kata laluan", "vi": "Mật khẩu", "th": "รหัสผ่าน", "tl": "Password", "hu": "Jelszó", "bg": "Парола", "mk": "Лозинка", "ar": "كلمة المرور", "fa": "رمز عبور", "he": "סיסמה", "ur": "پاسورڈ", "hi": "पासवर्ड", "bn": "পাসওয়ার্ড", "ta": "கடவுச்சொல்", "te": "పాస్‌వర్డ్", "mr": "पासवर्ड"},
    "error.generic": {"tr": "Bir hata oluştu", "id": "Terjadi kesalahan", "ms": "Ralat berlaku", "vi": "Đã xảy ra lỗi", "th": "เกิดข้อผิดพลาด", "tl": "May naganap na error", "hu": "Hiba történt", "bg": "Възникна грешка", "mk": "Се појави грешка", "ar": "حدث خطأ", "fa": "خطایی رخ داد", "he": "אירעה שגיאה", "ur": "خرابی ہوئی", "hi": "एक त्रुटि हुई", "bn": "একটি ত্রুটি ঘটেছে", "ta": "ஒரு பிழை ஏற்பட்டது", "te": "ఒక లోపం సంభవించింది", "mr": "एक त्रुटी झाली"},
    "app.name": {"tr": "Danwa", "id": "Danwa", "ms": "Danwa", "vi": "Danwa", "th": "Danwa", "tl": "Danwa", "hu": "Danwa", "bg": "Danwa", "mk": "Danwa", "ar": "Danwa", "fa": "Danwa", "he": "Danwa", "ur": "Danwa", "hi": "Danwa", "bn": "Danwa", "ta": "Danwa", "te": "Danwa", "mr": "Danwa", "sa": "Danwa"},
}


def build_translations(locale: str) -> dict:
    """Build translation dict for a locale from all translation sources."""
    result = {}
    for src in [_ROMANCE, _GERMANIC, _SLAVIC, _CJK, _OTHER]:
        for key, locale_map in src.items():
            if locale in locale_map:
                result[key] = locale_map[locale]
    return result


ALL_LOCALES = [
    "bn", "bo", "br", "cz", "da", "de", "en", "eo", "es", "et", "eu",
    "fa", "fi", "fr", "ga", "hi", "hr", "hu", "hy", "id", "io", "is",
    "it", "iu", "ja", "ka", "ku", "la", "lt", "lv", "mi", "mk", "mr",
    "ms", "nb", "nl", "nn", "pl", "pt", "ro", "ru", "sa", "sk", "sl",
    "sq", "sr", "ta", "te", "th", "tl", "tr", "ur", "vi", "yi", "zh",
]


def generate(locale: str) -> None:
    en = json.loads(EN_SOURCE.read_text(encoding="utf-8"))
    translations = build_translations(locale)

    result = {}
    for key in en:
        result[key] = translations.get(key, en[key])

    out_dir = ROOT / "ui-translations" / f"lang-{locale}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ui_strings.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    translated_count = len(translations)
    print(f"[{locale}] {len(result)} keys ({translated_count} translated, {len(result) - translated_count} fallback)")


def generate_all() -> None:
    for locale in ALL_LOCALES:
        if locale == "en":
            continue  # en is the source
        if locale == "de":
            continue  # de is from de.js
        generate(locale)
    print(f"\nDone. Generated {len(ALL_LOCALES) - 2} translation files.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        generate_all()
    elif len(sys.argv) > 1:
        generate(sys.argv[1])
    else:
        print("Usage:")
        print("  python scripts/generate_translations.py --all")
        print("  python scripts/generate_translations.py fr")
