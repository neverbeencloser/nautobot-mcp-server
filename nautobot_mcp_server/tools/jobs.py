"""Job-related tools for Nautobot MCP Server."""

from typing import Any, Optional

from mcp.server.fastmcp import Context, FastMCP

from .base import NautobotToolBase


class JobTools(NautobotToolBase):
    """Tools for managing jobs in Nautobot."""

    def register(self, mcp: FastMCP):
        """Register job tools with the MCP server.

        Args:
            mcp: FastMCP instance to register tools with
        """

        @mcp.tool()
        def nautobot_list_jobs(ctx: Context, limit: int = 20) -> str:
            """List all available jobs in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                limit: Number of jobs to return (default: 20)

            Returns:
                JSON string of job list
            """
            ctx.info(f"Listing jobs (limit={limit})")

            try:
                client = self._get_client()
                jobs = client.extras.jobs.filter(limit=limit)

                result = []
                for job in jobs:
                    job_info = {
                        "id": str(job.id),
                        "name": job.name,
                        "slug": job.slug if hasattr(job, "slug") else None,
                        "description": job.description if hasattr(job, "description") else None,
                        "module_name": job.module_name if hasattr(job, "module_name") else None,
                        "job_class_name": job.job_class_name if hasattr(job, "job_class_name") else None,
                        "enabled": job.enabled if hasattr(job, "enabled") else True,
                        "has_sensitive_variables": job.has_sensitive_variables
                        if hasattr(job, "has_sensitive_variables")
                        else False,
                    }
                    result.append(job_info)

                ctx.info(f"Found {len(result)} jobs")
                return self.format_success(result)

            except Exception as e:
                return self.log_and_return_error(ctx, "listing jobs", e)

        @mcp.tool()
        def nautobot_get_job(ctx: Context, job_id: str) -> str:
            """Get a specific job by ID, name, or slug.

            Args:
                ctx: MCP context for logging and progress
                job_id: Job ID (UUID), name, or slug

            Returns:
                JSON string of job details
            """
            ctx.info(f"Getting job: {job_id}")

            try:
                client = self._get_client()
                jobs = client.extras.jobs

                # Try to get by ID first (UUID)
                try:
                    job = jobs.get(job_id)
                    ctx.debug(f"Found job by ID: {job_id}")
                except Exception:
                    # If not found by ID, search by name or slug
                    all_jobs = jobs.all()
                    job = None
                    for j in all_jobs:
                        if j.name == job_id or (hasattr(j, "slug") and j.slug == job_id):
                            job = j
                            ctx.debug(f"Found job by name/slug: {job_id}")
                            break

                if job:
                    job_info = {
                        "id": str(job.id),
                        "name": job.name,
                        "slug": job.slug if hasattr(job, "slug") else None,
                        "description": job.description if hasattr(job, "description") else None,
                        "module_name": job.module_name if hasattr(job, "module_name") else None,
                        "job_class_name": job.job_class_name if hasattr(job, "job_class_name") else None,
                        "enabled": job.enabled if hasattr(job, "enabled") else True,
                        "has_sensitive_variables": job.has_sensitive_variables
                        if hasattr(job, "has_sensitive_variables")
                        else False,
                        "supports_dryrun": job.supports_dryrun if hasattr(job, "supports_dryrun") else False,
                        "approval_required": job.approval_required if hasattr(job, "approval_required") else False,
                        "soft_time_limit": job.soft_time_limit if hasattr(job, "soft_time_limit") else None,
                        "time_limit": job.time_limit if hasattr(job, "time_limit") else None,
                    }

                    ctx.info(f"Successfully retrieved job: {job.name}")
                    return self.format_success(job_info)
                else:
                    ctx.warning(f"Job not found: {job_id}")
                    return self.format_error(f"Job not found: {job_id}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting job", e)

        @mcp.tool()
        def nautobot_run_job(ctx: Context, job_name: str, **kwargs: Any) -> str:
            """Run a job in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                job_name: Name, slug, or ID of the job to run
                **kwargs: Additional job parameters

            Returns:
                JSON string with job execution details
            """
            ctx.info(f"Running job: {job_name}")

            try:
                client = self._get_client()
                jobs = client.extras.jobs

                # Get the job
                ctx.debug(f"Looking up job: {job_name}")
                try:
                    job = jobs.get(job_name)
                    ctx.debug(f"Found job by ID: {job_name}")
                except Exception:
                    # Search by name or slug
                    all_jobs = jobs.all()
                    job = None
                    for j in all_jobs:
                        if j.name == job_name or (hasattr(j, "slug") and j.slug == job_name):
                            job = j
                            ctx.debug(f"Found job by name/slug: {job_name}")
                            break

                if not job:
                    ctx.error(f"Job not found: {job_name}")
                    return self.format_error(f"Job not found: {job_name}")

                # Check if job is enabled
                if hasattr(job, "enabled") and not job.enabled:
                    ctx.error(f"Job is disabled: {job_name}")
                    return self.format_error(f"Job is disabled: {job_name}")

                # Run the job
                ctx.info(f"Executing job with parameters: {kwargs}")

                # Handle common job parameters
                job_kwargs = {}
                if "commit" in kwargs:
                    job_kwargs["commit"] = bool(kwargs["commit"])
                if "dryrun" in kwargs:
                    job_kwargs["dryrun"] = bool(kwargs["dryrun"])

                # Add any other parameters
                for key, value in kwargs.items():
                    if key not in ["commit", "dryrun"]:
                        job_kwargs[key] = value

                result = job.run(**job_kwargs)

                job_result_info = {
                    "job_name": job.name,
                    "job_id": str(job.id),
                    "result_id": str(result.id) if hasattr(result, "id") else None,
                    "status": "Job started",
                    "parameters": job_kwargs,
                }

                ctx.info(f"Successfully started job: {job.name}")
                return self.format_success(job_result_info, message=f"Job '{job.name}' started successfully")

            except Exception as e:
                return self.log_and_return_error(ctx, "running job", e)

        @mcp.tool()
        def nautobot_list_job_results(
            ctx: Context, limit: int = 10, job_name: Optional[str] = None, status: Optional[str] = None
        ) -> str:
            """List job results in Nautobot.

            Args:
                ctx: MCP context for logging and progress
                limit: Number of job results to return (default: 10)
                job_name: Filter by job name (optional)
                status: Filter by status (optional)

            Returns:
                JSON string of job result list
            """
            ctx.info(f"Listing job results (limit={limit}, job_name={job_name}, status={status})")

            try:
                client = self._get_client()
                job_results = client.extras.job_results

                # Apply filters
                filters = {"limit": limit}
                if job_name:
                    filters["job_model__name"] = job_name
                if status:
                    filters["status"] = status

                results = job_results.filter(**filters)

                result_list = []
                for result in results:
                    result_info = {
                        "id": str(result.id),
                        "name": result.name if hasattr(result, "name") else None,
                        "job": str(result.job) if hasattr(result, "job") else None,
                        "status": str(result.status) if hasattr(result, "status") else None,
                        "created": str(result.created) if hasattr(result, "created") else None,
                        "completed": str(result.completed) if hasattr(result, "completed") else None,
                        "user": str(result.user) if hasattr(result, "user") else None,
                        "task_kwargs": result.task_kwargs if hasattr(result, "task_kwargs") else None,
                    }
                    result_list.append(result_info)

                ctx.info(f"Found {len(result_list)} job results")
                return self.format_success(result_list)

            except Exception as e:
                return self.log_and_return_error(ctx, "listing job results", e)

        @mcp.tool()
        def nautobot_get_job_result(ctx: Context, result_id: str) -> str:
            """Get a specific job result by ID.

            Args:
                ctx: MCP context for logging and progress
                result_id: Job result ID (UUID)

            Returns:
                JSON string of job result details
            """
            ctx.info(f"Getting job result: {result_id}")

            try:
                client = self._get_client()
                job_results = client.extras.job_results

                result = job_results.get(id=result_id)

                if result:
                    result_info = {
                        "id": str(result.id),
                        "name": result.name if hasattr(result, "name") else None,
                        "job": str(result.job) if hasattr(result, "job") else None,
                        "status": str(result.status) if hasattr(result, "status") else None,
                        "created": str(result.created) if hasattr(result, "created") else None,
                        "completed": str(result.completed) if hasattr(result, "completed") else None,
                        "user": str(result.user) if hasattr(result, "user") else None,
                        "task_kwargs": result.task_kwargs if hasattr(result, "task_kwargs") else None,
                        "job_id": str(result.job_id) if hasattr(result, "job_id") else None,
                        "date_done": str(result.date_done) if hasattr(result, "date_done") else None,
                        "traceback": result.traceback if hasattr(result, "traceback") else None,
                        "result": result.result if hasattr(result, "result") else None,
                    }

                    ctx.info(f"Successfully retrieved job result: {result_id}")
                    return self.format_success(result_info)
                else:
                    ctx.warning(f"Job result not found: {result_id}")
                    return self.format_error(f"Job result not found: {result_id}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting job result", e)

        @mcp.tool()
        def nautobot_get_job_logs(ctx: Context, result_id: str) -> str:
            """Get logs for a specific job result.

            Args:
                ctx: MCP context for logging and progress
                result_id: Job result ID (UUID)

            Returns:
                JSON string of job logs
            """
            ctx.info(f"Getting job logs for result: {result_id}")

            try:
                client = self._get_client()
                job_results = client.extras.job_results

                result = job_results.get(id=result_id)

                if result:
                    log_info = {
                        "job_result_id": str(result.id),
                        "job_name": result.name if hasattr(result, "name") else None,
                        "status": str(result.status) if hasattr(result, "status") else None,
                        "logs": result.log if hasattr(result, "log") else "",
                    }

                    # Also include general result info
                    if hasattr(result, "traceback") and result.traceback:
                        log_info["traceback"] = result.traceback

                    ctx.info(f"Successfully retrieved logs for job result: {result_id}")
                    return self.format_success(log_info, message="Job logs retrieved successfully")
                else:
                    ctx.warning(f"Job result not found: {result_id}")
                    return self.format_error(f"Job result not found: {result_id}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting job logs", e)
