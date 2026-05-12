import requests
import warnings
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import tkinter as tk
import webbrowser
from pathlib import Path
from datetime import datetime

def fetch_public_profile_html(username): 
    """Gets HTML of an Instagram page with `username`."""
    url = f"https://www.instagram.com/{username}/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/116.0 Safari/537.36"
        ))
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()
            
    return html

def extract_post_urls(html, username):
    """Gets the Instagram post links from an account's HTML. """
    soup = BeautifulSoup(html, "html.parser")
    found = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith(f"/{username}/p/"): #or href.startswith("/reel/") or href.startswith("/tv/"):
            full_url = urljoin("https://www.instagram.com", href.split("?", 1)[0])
            found.add(full_url)

    if len(found) == 0:
        def custom_formatwarning(message, category, filename, lineno, line=None):
            return f"{message}\n"

        warnings.formatwarning = custom_formatwarning
        warnings.warn(f"\033[1m\033[93mNo posts extracted from account \"{username}\". Confirm that the account is public and wait a few minutes before trying again.\033[0m", UserWarning, stacklevel=0)

    return sorted(found)

def remove_urls_in_history(urls):
    """Removes all urls from `urls` found in "history.sh". """
    history = set()
    with open(Path("history.sh"), "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                history.add(line)
    return [url for url in urls if url not in history]

def get_usernames():
    """Gets all usernames found in "history.sh". """
    lines_array = []

    with open("accounts.sh", "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                lines_array.append(stripped)

    return lines_array

def select_urls(urls):
    """GUI for selecting all Instagram URLs not found in history. """
    checked_urls = []

    def save_checked_urls(checked_urls):
        if not checked_urls:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        txt_path = Path("history.sh")

        with open(txt_path, "a", encoding="utf-8") as f:
            f.write(f"# {timestamp}\n")
            for url in checked_urls:
                f.write(f"{url}\n")
            f.write("\n")

    def open_url(url):
        webbrowser.open(url)

    def finish():
        nonlocal checked_urls
        checked_urls = [
            url for url, var in url_vars.items()
            if var.get() == 1
        ]
        save_checked_urls(checked_urls)
        root.destroy()

    root = tk.Tk()
    root.title("Select URLs")
    root.geometry("900x500")

    url_vars = {}

    # Header row
    header = tk.Frame(root)
    header.pack(fill="x", padx=10, pady=(10, 0))

    tk.Label(header, text="Seen", width=8, font=("Arial", 10, "bold")).pack(side="left")
    tk.Label(header, text="Post URL", font=("Arial", 10, "bold")).pack(side="left")

    # Scrollable area container
    container = tk.Frame(root)
    container.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(container)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Rows
    for url in urls:
        row = tk.Frame(scrollable_frame)
        row.pack(anchor="w", fill="x", pady=2)

        var = tk.IntVar()
        tk.Checkbutton(row, variable=var, width=8).pack(side="left")

        link = tk.Label(
            row,
            text=url,
            fg="blue",
            cursor="hand2",
            font=("Arial", 10, "underline"),
            anchor="w",
            justify="left"
        )
        link.pack(side="left", fill="x", expand=True)
        link.bind("<Button-1>", lambda e, u=url: open_url(u))

        url_vars[url] = var

    # Optional mouse wheel support
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Done button
    tk.Button(root, text="Done", command=finish).pack(pady=10)

    root.mainloop()
    return checked_urls

def main():
    usernames = get_usernames()
    # usernames = ["a"]
    assert len(usernames) > 0, "You must have at least one username in \"accounts.sh\"."

    try:
        post_urls_all = []
        for username in usernames:
            html = fetch_public_profile_html(username)
            post_urls = extract_post_urls(html, username)
            # post_urls = ['https://www.instagram.com/matt.lyttle/p/DVtVh2QDduk/', 'https://www.instagram.com/matt.lyttle/p/DX1gWWijhV0/', 'https://www.instagram.com/matt.lyttle/p/DX7O91aEZZp/', 'https://www.instagram.com/matt.lyttle/p/DX8D3LatiFj/', 'https://www.instagram.com/matt.lyttle/p/DXmCqtGjv8f/', 'https://www.instagram.com/matt.lyttle/p/DXrlSTXDrXk/', 'https://www.instagram.com/matt.lyttle/p/DXvLS4mEX4X/', 'https://www.instagram.com/matt.lyttle/p/DXzLMvoDnFP/', 'https://www.instagram.com/matt.lyttle/p/DYD3hlxjeH3/']
            post_urls = remove_urls_in_history(post_urls)
            if len(post_urls) > 0:
                post_urls_all.extend(post_urls)
            post_urls_all
        select_urls(post_urls_all)

    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.RequestException as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    main()