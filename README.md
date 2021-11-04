# Digital Notebook
A python program using sqlite3 for storing and conviniently retrieving everyday information.

Currently stores todos, events and passwords.

## Todos
A todo with a name, description and priority (4 priority options)

## Events
Event with a name/description date, an optional duration, convinient ways to query them by date.

## Passwords

A password with a domain/username. Optionally generates long secure passwords. Copies passwords to clipboard when queried.


# Installation
`makepkg -si`
`pip3 install -r requirements.txt`

# Examples

`digital-notebook events get --min-date 'now' --max-date 'in a day'`

Get events that will happen in the next 24 hours.

`digital-notebook todo g eat`

Get all todos whos name include 'eat'.

`digital-notebook passwords get gmail.com`

Finds and copies to clipboard (without printing) your password to gmail.

Sqlite3 file in `~/.digital-notebook/data.sqlite3`.

# Future:
Initialization is slow (importing `dateparser` takes like 0.2 seconds).

Add example output images.

Some sort of a way to merge 2 databases.

Add documentation to command line arguments.
