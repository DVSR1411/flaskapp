resource "aws_iam_role" "kubectl_role" {
  name = "KubectlRole"
  depends_on = [ aws_iam_role.CodeBuildServiceRole ]
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.CodeBuildServiceRole.arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_role_policy" "kubectl_policy" {
  name = "kubectl-access"
  role = aws_iam_role.kubectl_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:Describe*"
        ]
        Resource = "*"
      }
    ]
  })
}
output "kubectl_role_arn" {
  value = aws_iam_role.kubectl_role.arn
  description = "Codebuild and eks"
}