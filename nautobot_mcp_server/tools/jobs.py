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
                job_list = client.extras.jobs.filter(limit=limit, depth=1)

                ctx.info(f"Found {len(job_list)} jobs")
                return self.format_success([dict(job) for job in job_list])

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
                    ctx.info(f"Successfully retrieved job: {job.name}")
                    return self.format_success(dict(job))
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

                ctx.info(f"Successfully started job: {job.name}")
                return self.format_success(dict(result), message=f"Job '{job.name}' started successfully")

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

                ctx.info(f"Found {len(results)} job results")
                return self.format_success([dict(result) for result in results])

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
                    ctx.info(f"Successfully retrieved job result: {result_id}")
                    return self.format_success(dict(result))
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
                    ctx.info(f"Successfully retrieved logs for job result: {result_id}")
                    return self.format_success(dict(result), message="Job logs retrieved successfully")
                else:
                    ctx.warning(f"Job result not found: {result_id}")
                    return self.format_error(f"Job result not found: {result_id}")

            except Exception as e:
                return self.log_and_return_error(ctx, "getting job logs", e)
