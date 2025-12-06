package main

import (
	"database/sql"
	"fmt"
	"os"

	_ "github.com/glebarez/go-sqlite"
)

func main() {
	fpath := "../../backend/sql_app.db"

	// checke if file exists
	_, err := os.Stat(fpath)
	if os.IsNotExist(err) {
		panic("file does not exist")
	}

	db, err := sql.Open("sqlite", fpath)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Print comprehensive database schema
	printDatabaseSchema(db)

	fmt.Println("\n" + repeatString("═", 80))
}

// IndexInfo holds information about a database index
type IndexInfo struct {
	Name       string
	TableName  string
	SQL        sql.NullString
	ColumnName string
}

// repeatString repeats a string n times
func repeatString(s string, n int) string {
	result := ""
	for i := 0; i < n; i++ {
		result += s
	}
	return result
}

// TableColumn represents a column in a database table
type TableColumn struct {
	CID          int
	Name         string
	Type         string
	NotNull      bool
	DefaultValue sql.NullString
	PK           bool
}

// printDatabaseSchema displays all tables with their columns and indexes
func printDatabaseSchema(db *sql.DB) {
	fmt.Println("\n" + repeatString("═", 80))
	fmt.Println("📊 DATABASE SCHEMA - TABLES, COLUMNS & INDEXES")
	fmt.Println(repeatString("═", 80))

	// Get all tables
	tables, err := db.Query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
	if err != nil {
		panic(err)
	}
	defer tables.Close()

	var tableNames []string
	for tables.Next() {
		var tableName string
		if err := tables.Scan(&tableName); err != nil {
			panic(err)
		}
		tableNames = append(tableNames, tableName)
	}

	// Process each table
	for i, tableName := range tableNames {
		if i > 0 {
			fmt.Println() // Add spacing between tables
		}

		fmt.Printf("\n┌─ 📋 Table: %s\n", tableName)
		fmt.Println(repeatString("─", 80))

		// Get column information using PRAGMA table_info
		pragmaQuery := fmt.Sprintf("PRAGMA table_info('%s');", tableName)
		columns, err := db.Query(pragmaQuery)
		if err != nil {
			panic(err)
		}

		var tableColumns []TableColumn
		for columns.Next() {
			var col TableColumn
			var notNullInt, pkInt int
			if err := columns.Scan(&col.CID, &col.Name, &col.Type, &notNullInt, &col.DefaultValue, &pkInt); err != nil {
				panic(err)
			}
			col.NotNull = notNullInt == 1
			col.PK = pkInt > 0
			tableColumns = append(tableColumns, col)
		}
		columns.Close()

		// Display columns
		fmt.Println("│")
		fmt.Println("├─ 📝 COLUMNS:")
		if len(tableColumns) == 0 {
			fmt.Println("│  └─ No columns found")
		} else {
			for j, col := range tableColumns {
				isLast := j == len(tableColumns)-1
				prefix := "├─"
				if isLast {
					prefix = "└─"
				}

				// Build column info string
				colInfo := fmt.Sprintf("%s %s (%s)", prefix, col.Name, col.Type)

				// Add constraints
				var constraints []string
				if col.PK {
					constraints = append(constraints, "PRIMARY KEY")
				}
				if col.NotNull && !col.PK {
					constraints = append(constraints, "NOT NULL")
				}
				if col.DefaultValue.Valid {
					constraints = append(constraints, fmt.Sprintf("DEFAULT: %s", col.DefaultValue.String))
				}

				if len(constraints) > 0 {
					colInfo += fmt.Sprintf(" [%s]", joinStrings(constraints, ", "))
				}

				fmt.Printf("│  %s\n", colInfo)
			}
		}

		// Get indexes for this table
		indexes, err := db.Query(
			"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name=? ORDER BY name;",
			tableName,
		)
		if err != nil {
			panic(err)
		}

		var indexInfos []IndexInfo
		for indexes.Next() {
			var info IndexInfo
			if err := indexes.Scan(&info.Name, &info.SQL); err != nil {
				panic(err)
			}
			info.TableName = tableName
			indexInfos = append(indexInfos, info)
		}
		indexes.Close()

		// Display indexes
		fmt.Println("│")
		fmt.Println("└─ 🔍 INDEXES:")
		if len(indexInfos) == 0 {
			fmt.Println("   └─ No indexes found")
		} else {
			for j, idx := range indexInfos {
				isLast := j == len(indexInfos)-1
				prefix := "├─"
				if isLast {
					prefix = "└─"
				}

				// Determine index type
				indexType := "Implicit"
				if idx.SQL.Valid && idx.SQL.String != "" {
					indexType = "Explicit"
				}

				// Get columns for this index
				pragmaQuery := fmt.Sprintf("PRAGMA index_info('%s');", idx.Name)
				colRows, err := db.Query(pragmaQuery)
				if err != nil {
					panic(err)
				}

				var indexColumns []string
				for colRows.Next() {
					var seqno, cid int
					var name string
					if err := colRows.Scan(&seqno, &cid, &name); err != nil {
						panic(err)
					}
					indexColumns = append(indexColumns, name)
				}
				colRows.Close()

				// Print index info
				fmt.Printf("   %s %s (%s) on [%s]\n",
					prefix,
					idx.Name,
					indexType,
					joinStrings(indexColumns, ", "),
				)

				// Optionally show SQL for explicit indexes
				if idx.SQL.Valid && idx.SQL.String != "" && !isLast {
					fmt.Printf("   │  └─ SQL: %s\n", idx.SQL.String)
				} else if idx.SQL.Valid && idx.SQL.String != "" && isLast {
					fmt.Printf("      └─ SQL: %s\n", idx.SQL.String)
				}
			}
		}
	}

	fmt.Println("\n" + repeatString("═", 80))
}

// joinStrings joins a slice of strings with a separator
func joinStrings(strs []string, sep string) string {
	if len(strs) == 0 {
		return ""
	}
	result := strs[0]
	for i := 1; i < len(strs); i++ {
		result += sep + strs[i]
	}
	return result
}
