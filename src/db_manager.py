"""
Script principal pour la gestion de la base de données des joueurs Valorant.
Ce script fournit une interface en ligne de commande pour toutes les opérations de base de données.
"""

import argparse
from database_utils import DatabaseManager
from rich.console import Console

console = Console()

def show_database_info():
    """Affiche les informations sur la base de données."""
    db_manager = DatabaseManager()
    db_manager.display_database_info()

def migrate_csv_to_db():
    """Migre les données depuis le CSV vers la base de données."""
    console.print("[bold blue]=== Migration CSV vers Base de données ===[/bold blue]")
    db_manager = DatabaseManager()
    success = db_manager.migrate_from_csv()
    
    if success:
        console.print("[green]Migration réussie ![/green]")
    else:
        console.print("[red]Échec de la migration[/red]")

def test_random_selection(count: int = 5):
    """Teste la sélection aléatoire de joueurs."""
    console.print(f"[bold blue]=== Test de sélection de {count} joueurs aléatoires ===[/bold blue]")
    
    db_manager = DatabaseManager()
    random_players = db_manager.get_random_players(count)
    
    if not random_players.empty:
        console.print(f"[green]✓ {len(random_players)} joueurs sélectionnés:[/green]")
        for i, (_, player) in enumerate(random_players.iterrows(), 1):
            console.print(f"  {i}. {player['name']} ({player['puuid'][:8]}...)")
    else:
        console.print("[red]✗ Aucun joueur trouvé[/red]")

def add_test_player():
    """Ajoute un joueur de test."""
    console.print("[bold blue]=== Ajout d'un joueur de test ===[/bold blue]")
    
    db_manager = DatabaseManager()
    test_name = "TestPlayer_CLI"
    test_puuid = "test-cli-puuid-12345678"
    
    if db_manager.add_player(test_name, test_puuid):
        console.print(f"[green]✓ Joueur de test '{test_name}' ajouté avec succès[/green]")
    else:
        console.print(f"[yellow]~ Joueur de test '{test_name}' déjà existant ou erreur[/yellow]")

def reset_database():
    """Recrée la base de données (attention: supprime toutes les données)."""
    console.print("[bold red]=== ATTENTION: Suppression de toutes les données ===[/bold red]")
    
    confirm = console.input("[yellow]Êtes-vous sûr de vouloir supprimer toutes les données ? (tapez 'OUI' pour confirmer): [/yellow]")
    
    if confirm != "OUI":
        console.print("[blue]Opération annulée[/blue]")
        return
    
    db_manager = DatabaseManager()
    
    try:
        # Supprimer le fichier de base de données
        if db_manager.db_path.exists():
            db_manager.db_path.unlink()
            console.print("[green]✓ Base de données supprimée[/green]")
        
        # Recréer la table
        if db_manager.create_players_table():
            console.print("[green]✓ Nouvelle base de données créée[/green]")
        else:
            console.print("[red]✗ Erreur lors de la création de la nouvelle base[/red]")
            
    except Exception as e:
        console.print(f"[red]Erreur lors de la suppression: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(
        description="Gestionnaire de base de données des joueurs Valorant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python db_manager.py --info                    # Afficher les infos de la BDD
  python db_manager.py --migrate                 # Migrer depuis CSV
  python db_manager.py --test-selection 10       # Tester sélection de 10 joueurs
  python db_manager.py --add-test               # Ajouter un joueur de test
  python db_manager.py --reset                   # Supprimer toutes les données
        """
    )
    
    parser.add_argument('--info', action='store_true',
                       help='Afficher les informations sur la base de données')
    
    parser.add_argument('--migrate', action='store_true',
                       help='Migrer les données depuis le fichier CSV vers la base de données')
    
    parser.add_argument('--test-selection', type=int, metavar='N',
                       help='Tester la sélection de N joueurs aléatoires')
    
    parser.add_argument('--add-test', action='store_true',
                       help='Ajouter un joueur de test à la base de données')
    
    parser.add_argument('--reset', action='store_true',
                       help='ATTENTION: Supprimer toutes les données et recréer la base')
    
    args = parser.parse_args()
    
    # Si aucun argument, afficher l'aide
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Exécuter les commandes
    if args.info:
        show_database_info()
    
    if args.migrate:
        migrate_csv_to_db()
    
    if args.test_selection is not None:
        test_random_selection(args.test_selection)
    
    if args.add_test:
        add_test_player()
    
    if args.reset:
        reset_database()

if __name__ == "__main__":
    main()
