"""
Script utilitaire pour afficher un résumé complet de l'état des données du projet Valorant.
"""

from database_utils import DatabaseManager
from config import MATCHS_FILE, DATA_FILE
from rich.console import Console
from rich.table import Table
import pandas as pd
from pathlib import Path

console = Console()

def check_database_status():
    """Vérifie l'état de la base de données des joueurs."""
    db_manager = DatabaseManager()
    
    if db_manager.database_exists():
        count = db_manager.get_player_count()
        status = f"[green]✓ {count} joueurs[/green]"
    else:
        status = "[red]✗ Vide ou inexistante[/red]"
    
    return status, db_manager.get_player_count() if db_manager.database_exists() else 0

def check_csv_file(file_path: Path, description: str):
    """Vérifie l'état d'un fichier CSV."""
    if file_path.exists():
        try:
            df = pd.read_csv(file_path)
            count = len(df)
            size_mb = file_path.stat().st_size / (1024 * 1024)
            status = f"[green]✓ {count} entrées ({size_mb:.1f} MB)[/green]"
            return status, count
        except Exception as e:
            status = f"[red]✗ Erreur: {str(e)[:30]}...[/red]"
            return status, 0
    else:
        status = "[yellow]⚠ Fichier inexistant[/yellow]"
        return status, 0

def display_data_summary():
    """Affiche un résumé complet des données."""
    console.print("[bold blue]🎮 Résumé des données Valorant[/bold blue]\n")
    
    # Créer un tableau pour l'affichage
    table = Table(title="État des fichiers de données")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Localisation", style="magenta")
    table.add_column("État", style="white")
    table.add_column("Nombre d'entrées", justify="right", style="green")
    
    # Vérifier la base de données des joueurs
    db_status, db_count = check_database_status()
    table.add_row("🗃️ Joueurs (BDD)", str(DATA_FILE / "player_stats.db"), db_status, str(db_count))
    
    # Vérifier le fichier CSV des matchs
    if MATCHS_FILE.exists():
        matchs_status, matchs_count = check_csv_file(MATCHS_FILE, "Matchs")
    else:
        matchs_status, matchs_count = "[yellow]⚠ Fichier inexistant[/yellow]", 0
    table.add_row("🎮 Matchs (CSV)", str(MATCHS_FILE), matchs_status, str(matchs_count))
    
    # Afficher le tableau
    console.print(table)
    
    # Afficher des recommandations
    console.print("\n[bold yellow]💡 Recommandations:[/bold yellow]")
    
    if db_count == 0:
        console.print("  • [red]Aucun joueur dans la base de données[/red]")
    
    if matchs_count == 0:
        console.print("  • [yellow]Aucun match collecté[/yellow]")
        console.print("    → Exécutez: [cyan]python matchs_collect.py[/cyan]")
    
    
    # Afficher quelques statistiques supplémentaires
    console.print(f"\n[bold green]📈 Résumé numérique:[/bold green]")
    console.print(f"  • Joueurs dans la base de données: [green]{db_count}[/green]")
    console.print(f"  • Matchs collectés: [green]{matchs_count}[/green]")
    
    if db_count > 0 and matchs_count > 0:
        ratio = matchs_count / db_count
        console.print(f"  • Ratio matchs/joueur: [cyan]{ratio:.1f}[/cyan]")
    
    # Vérifier l'espace disque utilisé
    total_size = 0
    for file_path in [MATCHS_FILE, DATA_FILE / "player_stats.db"]:
        if file_path.exists():
            total_size += file_path.stat().st_size
    
    size_mb = total_size / (1024 * 1024)
    console.print(f"  • Espace total utilisé: [blue]{size_mb:.1f} MB[/blue]")

def show_recent_activity():
    """Affiche l'activité récente des fichiers."""
    console.print(f"\n[bold cyan]🕒 Activité récente:[/bold cyan]")
    
    files_to_check = [
        (DATA_FILE / "player_stats.db", "Base de données"),
        (MATCHS_FILE, "Fichier des matchs"),
    ]
    
    for file_path, description in files_to_check:
        if file_path.exists():
            mtime = file_path.stat().st_mtime
            import datetime
            last_modified = datetime.datetime.fromtimestamp(mtime)
            time_diff = datetime.datetime.now() - last_modified
            
            if time_diff.days == 0:
                time_str = f"{time_diff.seconds // 3600}h {(time_diff.seconds % 3600) // 60}m"
            else:
                time_str = f"{time_diff.days}j"
            
            console.print(f"  • {description}: [yellow]modifié il y a {time_str}[/yellow]")

def main():
    display_data_summary()
    show_recent_activity()
    
    console.print(f"\n[bold blue]🔧 Commandes utiles:[/bold blue]")
    console.print("  • [cyan]python db_manager.py --info[/cyan]          → Détails de la BDD")
    console.print("  • [cyan]python player_stats_collector.py[/cyan]     → Collecter des stats")
    console.print("  • [cyan]python matchs_collect.py[/cyan]             → Collecter des matchs")
    console.print("  • [cyan]python data_summary.py[/cyan]               → Ce résumé")

if __name__ == "__main__":
    main()
