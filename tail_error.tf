# ZD-115407 repro: failing precondition evaluated during plan, after the large
# main.tf diff is computed. Reproduces iHerb's shape: big plan output followed
# by a real error. The check_type expression fails the "list must be
# consistent" style structural check.

variable "sheets" {
  type    = list(string)
  default = ["sheet-a", "sheet-b", "sheet-c"]
}

resource "terraform_data" "tail_error" {
  input = var.sheets

  lifecycle {
    precondition {
      condition     = length(var.sheets) == length(distinct([for s in var.sheets : length(s)]))
      error_message = "Structural validation failed for input variable sheets: all list elements must have the same type."
    }
  }
}
