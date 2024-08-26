plan-infra:
	terraform plan -var-file=./dev.tfvars -out=./.terraform/dev.tfplan 

apply-infra:
	terraform apply ./.terraform/dev.tfplan

destroy-infra:
	terraform destroy -var-file=./dev.tfvars
