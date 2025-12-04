from typing import Dict, Optional
from urllib.parse import urlencode

from opa_client.errors import (
	CheckPermissionError,
)

async def my_check_permission(
		self,
		input_data: dict,
		policy_name: str,
		rule_name: str,
		query_params: Optional[Dict[str, bool]] = None,
	) -> dict:
		"""
		Check permissions based on input data, policy name, and rule name.

		Parameters:
			input_data (dict): The input data to check against the policy.
			policy_name (str): The name of the policy.
			rule_name (str): The name of the rule in the policy.
			query_params (Dict[str, bool], optional): Query parameters.

		Returns:
			dict: The result of the permission check.
		"""
		policy = await self.get_policy(policy_name)
		ast = policy.get("result", {}).get("ast", {})
		package_path = "/".join(
			[p.get("value") for p in ast.get("package", {}).get("path", [])]
		)
		rules = [
			rule.get("head", {}).get("name") for rule in ast.get("rules", [])
		]

		if rule_name not in rules:
			raise CheckPermissionError(
				expression="resource_not_found",
				message=f"Rule '{rule_name}' not found in policy '{policy_name}'"
			)

		# I modified the URL.
		# In the original library it is: 
		# url = f"{self.root_url}/data/{package_path}/{rule_name}"
		# However, it does not return anything due to "data".
		# Hence, the new URL is defined as follows:
		url = f"{self.root_url}/{package_path}/{rule_name}"
		if query_params:
			url = f"{url}?{urlencode(query_params)}"

		async with self._session.post(
			url, json={"input": input_data}
		) as response:
			response.raise_for_status()
			return await response.json()
