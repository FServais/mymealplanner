package main

import (
	"os"

	cli "github.com/fservais/mymealplanner/tools/cli/internal/cli"
)

func main() {
	if err := cli.Execute(); err != nil {
		os.Exit(1)
	}
}
