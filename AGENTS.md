# Sales data pipeline: shared instructions for Codex and Kiro

## User preferences and scope

- The user is doing an AWS internship project and needs to explain the work in a university report.
- help_level: HIGH, explicitly selected by the user. Explain steps, reasons, results, and limitations in Vietnamese. Do not ask the help-level question again.
- The user has authorized Codex and Kiro to cooperate on this project using its local files and explicit handoffs.
- Current user task explicitly authorizes implementing stages A–F of the sales pipeline, including checking existing AWS resources, updating its Lambda code when justified, and creating the requested Glue Catalog/Athena/CloudWatch components. Keep all regional resources in ap-southeast-2 and do not recreate or delete existing resources without a concrete need. The Hugo report remains separate.
- Workspace: `D:/AWS/sales-data-pipeline`.
- Local AWS profile: `codex-aws`. Selected Region: `ap-southeast-2`.
- Prefer the configured `aws-mcp` tools for AWS operations. Local CLI commands must explicitly use `--profile codex-aws --region ap-southeast-2` where applicable.

## Coordination

- Read `docs/codex-kiro-handoff.md` before starting work, and re-read files another agent has changed before editing them.
- Record the current task, responsible agent, and exact files being edited in the handoff before changing application files. Work sequentially when the same file is involved.
- Preserve the user's edits and the other agent's work. Git was initialized on 2026-10-22; main tracks https://github.com/tuanpham2005/sales-data-pipeline.git (public). Inspect status/diff before editing; do not reset, restore, or clean other people's changes.
- At handoff, record changed files, commands actually run, actual results, unresolved issues, and the next action. Distinguish local evidence from AWS evidence.
- Codex can open the workspace/files using the installed Kiro launcher. This installed Kiro 1.2.4 advertises `kiro chat`, but an actual attempt failed with `workbench.action.chat.newChat` not found. Do not use a zero exit status to claim a prompt was delivered. The user must submit the initial handoff request in Kiro's chat until a supported direct channel is verified.
- Use saved files for the return channel. Do not claim a live, automatic chat bridge or completion by the other agent without evidence.

## Project facts and verification

- Read `README.md` and `README_LAMBDA.md` for the existing local pipeline and Lambda adapter.
- Core processing lives in `src/pipeline.py`; the AWS adapter is `lambda_function.py`.
- Existing check: `python -m unittest discover -s tests -v`.
- Existing package build: `python build_lambda.py`. Building a ZIP does not deploy it.
- Sample baseline: 10 input rows, 6 valid, 4 rejected, total quantity 17, total revenue 670000.00 VND.
- Tests use a fake S3 client. Passing them does not prove deployed Lambda, IAM, or an S3 trigger works.
- Resource names in `README_LAMBDA.md` are configuration notes, not proof those resources currently exist in the connected AWS project.
- Keep credentials and login caches outside the repository. The shared profile name is sufficient; do not copy credentials into source or handoff files.

<!-- BEGIN AWS Agent Toolkit rules -->
# AWS Guidance for the new AWS experience

This user has signed up for the new AWS experience. This experience lets you sign into AWS using a social provider and requires the following additional context.

Where this guidance conflicts with the project's own instructions, the project's instructions take precedence.

## Context

### Terminology:

- Say "project" instead of "account" — a project contains an AWS account and settings for sharing with other collaborators
- Say "team member" instead of "IAM user" — users are invited by email, not created or federated in IAM
- Say "AWS Settings" when referring to management tasks at [settings.aws.com](https://settings.aws.com/) (project management, billing, team members, spend limits). Users view their actual AWS resources in the AWS Management Console.
- Say "selected Region" when referring to the user's Region — not "home Region"
- The user has a managed IAM experience. This includes a managed service control policies (SCP) and resource control policies (RCP) that govern the use of AWS. They will still need to use IAM to create policies to let services work with each other. If there are questions about the SCPs or RCPs, go to the documentation at https://docs.aws.amazon.com/accounts/latest/reference/scps-and-rcps-for-projects.html

### Constraints:

- All projects share a single AWS Region determined by the user's contact address. Resources cannot be created in other Regions
- When developing:
  - MUST create all Regional resources in the project's assigned Region
  - You CAN create AWS WAF and Cloudwatch Logs resources in us-east-1 when there are global resources (like a global WAF instance) that require a connection to dependencies in us-east-1. You should not use these for any other reason, because resources in the selected Region will provide lower cost (due to no cross-Region traffic), increased availability (due to no cross-Region traffic), and easier manageability (due to not needing to look in another Region). When you need to do an inventory of resources, you need to look in both the selected Region and us-east-1 for Cloudwatch Logs or WAF resources.
  - MUST NOT attempt to create Lambda, API Gateway, or other Regional resources in any other Region
  - MUST direct users to confirm their Region in AWS Settings > View all projects > Overview > Additional Info > Region. If the user cannot confirm their Region, check in ~/.aws/config
  - MUST NOT use Lambda@Edge — excluded from both Lambda and CloudFront
  - MUST NOT use CloudFormation StackSets — no multi-account or multi-Region deployments
  - MUST NOT attempt cross-Region actions — no cross-Region replication for DynamoDB/S3/RDS, no multi-Region KMS keys
  - MUST NOT use Route 53 cross-Region routing — geolocation, latency-based, and failover routing policies are not available
  - CloudFront is a global service and its actions ARE allowed in `us-east-1`. A user can create a CloudFront distribution pointing to their project-region Lambda function URL or API Gateway. However, Lambda and API Gateway themselves MUST NOT be created in `us-east-1` — they must be in the project Region.
  - Reduced availability in `eu-north-1` specifically: Amazon Rekognition, Amazon Textract, Amazon Personalize, AWS App Runner are not available in that Region.
- IAM permissions for human access are managed by AWS. Don't assign roles to team members unless absolutely necessary
- The user may have a spend limit if they are on the paid plan. The limit that pauses their project if it's exceeded. If resources suddenly become inaccessible, ask if they have a spend limit configured. Only project owners can modify a spend limit.
- When developing:
  - MUST ask about spend limit status if the user reports sudden "Access Denied" errors on operations that previously worked
  - MUST direct users to check spend status in AWS Settings > Billing
  - MUST check if a user has upgraded their account to the paid plan
  - MUST ask the user if they want to clean up the successfully created resources or keep them to reduce cost
- The user sets up billing, creates spend limits, and retrieves and pays invoices in AWS Settings. The user creates budgets and optimizes their costs in the AWS Billing and Cost Management console
- Not all AWS services are available. If a service isn't working, do the following:
  1. Run the command `aws freetier get-account-plan-state`
  2. If accountPlanType": "FREE", check the [Free Tier supported services list](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html#supported-services-free-tier) next,
  3. If accountPlanType": "PAID", check the [Paid Tier supported services list](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html#supported-services-paid-plan).
  4. If neither list shows the service, check the [Not supported for this experience list](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html#unsupported-services). The user will need to activate advanced features to access this service.
- Users can activate advanced AWS services and capabilities for their account.
- Before starting a task, check whether a relevant AWS skill is available. Load the skill with retrieve_skill and prefer its guidance over general knowledge.

### Help level

- help_level (required): LOW, MEDIUM, or HIGH. While a user is building, you MUST ask the user: "How much guidance would you like from me? Low (I only flag security risks), medium (I ask a couple of clarifying questions if something seems off), or high (I explain what I'm doing, suggest alternatives, and flag best practices)."

You CAN update this rule file to save a user's help_level.

Constraints for each level:

**LOW:**

- MUST follow all constraints in this context file
- MUST execute the user’s request without modification
- MUST NOT ask clarifying questions unless the action would create a security vulnerability
- MUST NOT suggest alternatives or improvements

**MEDIUM:**

- MUST execute the user's request
- MAY ask up to two clarifying questions per task if the request has an ambiguity or a potential issue
- MUST NOT repeat a question or suggestion the user has already dismissed
- MUST NOT explain trade-offs or alternatives unless the user asks

**HIGH:**

- MUST explain what each step does and why before executing it
- MUST suggest alternatives when a better approach exists
- MUST flag best practices and explain trade-offs
- MUST still execute the user's choice if they disagree with a suggestion

Local AWS profile: codex-aws. Selected Region: ap-southeast-2.
<!-- END AWS Agent Toolkit rules -->
