# LAB 02 - Build a High Availability Application Architecture.

In this hands-on lab, you'll deploy the CloudAlbum application with HA(high availability) architecture in the Amazon Web Services environment.

## In this lab cover.. 
* Configure VPC for the HA environment. (CloudFormation template will be provided.)
* Configure EFS for the scalable shared storage.
* Configure Elasticache - Redis for the session store.
* Configure ElasticBeanstalk
  * with RDS, ALB and AutoScaling 


## Prerequisites
The following prerequisited are required for this hands-on lab:

* AWS Console Access
* AWS CLI installed and configured on your EC2 or PC. (`AdministratorAccess` recommended)


## TASK 1. Create your multi-az VPC

In this section, you will create an VPC with multi-az for the high availability using CloudFormation.

<img src=./images/lab-ha-task1-cf-diagram.png width=700?>


1. Make sure the current region is Singapore (ap-souteeast-1).
 * <img src=./images/lab-ha-task1-region.png width=700>

2. In the AWS Console, click **Services**, then click **CloudFormation** to open the CloudFormation dashboard.

3. Click **Create Stack** button at the top-left corner. (or click **Create new stack** at the center of page.)

4. Download the **CloudFormation** template file (network.yaml) to your local laptop.
 * Download Link : https://github.com/aws-kr-tnc/moving-to-serverless-workshop-1d/blob/master/resources/network.yaml

5. On the **Select Tempalte** page, click **Upload a template to Amazon S3**. Click **Browse...** button. Then choose `network.yaml` file which is downloaded previous step.

6. Click **Next** button.

7. On the **Specify Details** page. Type `workshop-vpc` for **Stack name**. 

8. Review `Parameters` section. You can check the CIDR address for VPC and subnets. If you want, you can modify these values your own.

9. Click **Next** button.

10. On the **Options** page, just click **Next** button. 

11. On the **Review** page, click **Create** button. 

12. About 5 minutes later, the stack creation will be completed. Check the **Status** field. You can see that the value of Satus is `CREATE_COMPLETE`.

<img src=./images/lab-ha-task1-cf-complete.png width=700>

13. Explore the `outputs` tab. Copy the values of `outputs` tab to the your notepad for later use.


## TASK 2. Create EFS(Elastic File System)

In this section, you will create an EFS for the CloudAlbum application. 

Amazon Elastic File System (Amazon EFS) provides a simple, scalable, elastic file system for Linux-based workloads for use with AWS Cloud services and on-premises resources. It is built to scale on demand to petabytes without disrupting applications, growing and shrinking automatically as you add and remove files, so your applications have the storage they need – when they need it. It is designed to provide massively parallel shared access to thousands of Amazon EC2 instances, enabling your applications to achieve high levels of aggregate throughput and IOPS with consistent low latencies. Amazon EFS is a fully managed service that requires no changes to your existing applications and tools, providing access through a standard file system interface for seamless integration.


14. In the AWS Console, click **Services**, then click **EFS** to open the EFS dashboard console.

15. Click **Create file system** button.

16. On the **Configure file system access** page, choose your VPC . You can check the name of VPC, it should contain `moving-to-serverless`. Then you have to choose pair of subnets and please check the each Availibity Zone of subnet. You can refer to following screen caputure image.

<img src=./images/lab-ha-task2-efs-1.png width=700>


17. On the **Configure optional settings** page, type `moving-to-serverless` for key `Name` under **Add tags** section.

18. Then click **Next Step**. (Leave the remaining configuration as default.)

19. On the **Review and create** page, check the configuration then click **Create File System** button.

20. After a while, you will see that the **Mount target state** changes from **Creating** to **Available** on the **Mount targets** section.

21. If the **Mount target state** becomes **Available**, Copy the **File system ID** and paste it `notepad` for later use in TASK 5. 


* Move to the next TASK.


## TASK 3. Create Elasticache 
We'll create Amazon Elasticache - Redis to use as a session store for CloudAlbum application. By storing session data in a separate session store such Elasticache-Redis, we can improve our application from statefull to stateless.

Amazon ElastiCache offers fully managed Redis and Memcached. Seamlessly deploy, run, and scale popular open source compatible in-memory data stores. Build data-intensive apps or improve the performance of your existing apps by retrieving data from high throughput and low latency in-memory data stores. Amazon ElastiCache is a popular choice for Gaming, Ad-Tech, Financial Services, Healthcare, and IoT apps.

22. In the **AWS Managed Console**, on the **Service** menu, Click **ElastiCache**.

23. In the left navigation pane, click **Redis**.

24. Click **Create**.

 This will bring you to the **Create your Amazon ElastiCache cluster** page. **Do not choose** `Cluster Mode enabled`. 
 
 * Cluster engine : `Redis`
 * Redis settings
   * **Name** : `moving-to-serverless`
   * **Description** : `workshop`
   * **Engine version compatibility** : `5.0.0`
   * **Port** : `6379`
   * **Parameter group** : `default.redis5.0`
   * **Node Type** : chache.t2.micro (0.5 GiB)
   * **Number of replicas** : 2 


<img src=./images/lab-ha-task3-ec-1.png width=700>

25. In the **Advanced Redis settings** section, configure:
* **Multi-AZ with Auto-Failover** : [v] (checked)
* **Subnet  group** : `Create new`
* **Name** : `moving-to-serverless`
* **Description** : `workshop`
* **VPC ID** : You can refer to the **VPCId** in `Outputs` tab values of CloudFormation.(**step 13**). 
* **Subnets** : Choose two subnets with **PriSub1** and **PriSub2** in `Outputs` tab values of CloudFormation.(**step 13**). You can refer to the subnet id and CIDR block of **PriSub1** and **PriSub2**.
* **Preferred availability zone(s)** : `No preference`

<img src=./images/lab-ha-task3-ec-2.png width=700>

* Leave the remaining configuration as default.

26. Click **Create** button, at the bottom of the page.

27. After a while, you will see that the **Status** column changes from **Creating** to **Available** on the **Status** column.

28. Copy the **Primary Endpoint**  and paste it `notepad` for later use in TASK 5. 

 * <img src=./images/lab-ha-task3-ec-3.png width=500>

 * **NOTE**: You can click the refresh button in the dashboard, if your cluster status not changed.

## TASK 4. Confiugure ElasticBeanstalk.

We will now deploy the CloudAlbum application using ElasticBeanstalk. Our application will be  integrated EFS, Elasticache, RDS, ALB, and AutoScalingGroup via ElasticBeanstalk.

With Elastic Beanstalk, you can quickly deploy and manage applications in the AWS Cloud without having to learn about the infrastructure that runs those applications. Elastic Beanstalk reduces management complexity without restricting choice or control. You simply upload your application, and Elastic Beanstalk automatically handles the details of capacity provisioning, load balancing, scaling, and application health monitoring.

29. In the **AWS Management Console** on the **Service** menu, click Elastic Beanstalk.

30. At the top-right of screen, clikck **Create New Application**.

31. At the **Create New Application** window, configure the following:

* **Application Name** : `HA-CloudAlbum`
* **Description** : `Moving to AWS Serverless Workshop`

32. Click **Create** button.

33. At the **All Applications > HA-CloudAlbum** page, click the **Create one now**.

34. On the **Select environment tier**, page:

 * Select **Web server environment**. 
 
35. Click **Select** button.

36. In the **Create a web server environemnt** section, for **Description** type `Moving to AWS Serverless Workshop`

37. In the **Base configuration** section, configure the following:

* **Preconfigured plafform** : `Python` 
<img src=./images/lab-ha-task4-eb-python.png width=500>

* **Application code** : `Upload your code`

38. Choose `Sample application` button.

39. Click **Configure more options**.

40. In the **Configure HaCloudalbum-env** page : Change the **Configuration presets** from `Low cost(Free Tier eligible)` to `High avalability`.

 * **Configuration presets** : `High avalability`
 <img src=./images/lab-ha-task4-eb-preset.png width=400>

 * **NOTE**: We will start from `High availability` preset for the convenience. We need to change some configuration for our application. 

41. In the **Database** section, click **Modify**.

 * **NOTE**: Please note that creating the database with ElasticBeanstalk ties it to the life-cycle of the ElasticBeanstalk environment. If the database is required to persistent in the event of the ElasticBeanstalk environment, We need to remove it from ElasticBeanstalk environment. We would recommend creating a RDS instance outside of ElasticBeanstalk and then connecting the ElasticBeanstalk environment to this database.
 
 * Using Elastic Beanstalk with Amazon Relational Database Service. (https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.RDS.html)


42. In the **Database settings** section, configure following parameters.

 * **Username** : `serverless`
 * **Password** : `workshop`
 * **Retention** : `Delete`
 * **Availability** : `High (Multi-AZ)`
 <img src=./images/lab-ha-task4-eb-db.png width=500>

**NOTE:** Because it is a hands-on environment, not a real operating environment, select **'Delete'** for convenience.

43. Click **Save** button.

44. In the **Network** section, click **Modify**.

45. In the **Virtual private cloud (VPC)** section of **Modify network** page, choose a VPC which tagged 'moving-to-serverless'.

 *  <img src=./images/lab-ha-task4-eb-network.png width=500>

46. In the **Load balancer settings** section, configure followings.
 
 * **Visivility** : `Public`
 
 * Choose **Availability Zone** and **Subnet**. You can choose `Public Subnet - 1` and `Public Subnet -2`
  <img src=./images/lab-ha-task4-eb-alb.png width=700>


47. In the **Instance settings** section, configure followings.
 
 * Choose **Availability Zone** and **Subnet**. You can choose `Private Subnet - 1` and `Private Subnet -2`
  <img src=./images/lab-ha-task4-eb-instance.png width=700>

48. In the **Database settings** section, configure followings.
 
 * Choose **Availability Zone** and **Subnet**. You can choose `Private Subnet - 1` and `Private Subnet -2`
  <img src=./images/lab-ha-task4-eb-dbsubnet.png width=700>

49. Click **Save** button.

50. Click **Modify** button of **Instances** section in the **Configure HaCloudalbum-env** page.

51. Choose a default security group, in the **EC2 security groups** section in the **Modify instances** page.

* <img src=./images/lab-ha-task4-eb-instance-sg.png width=500>

52. Click **Create environment** button in the bottom of the page.

* **NOTE:** It will probably take 15 minutes or so. It is good to drink coffee for a while.

* <img src=./images/coffee-cup.png width=200>

* <div>Icons made by <a href="https://www.freepik.com/" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" 			    title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>


## TASK 5. Deploy Application with ElasticBeanstalk.

If the previous TASK was successfully completed, you will see the following screen.

 * <img src=./images/lab-ha-task5-eb-simpleapp.png  width=500> 

 * You can see the deployed application by clicking on the URL link in the top line.

 * <img src=./images/lab-ha-task5-eb-simpleapp-screen.png width=500> 

Now, let's deploy our application.


53. Click the **Configuration** button in the left navigation menu.

 * <img src=./images/lab-ha-task5-eb-configuration.png width=300>

* We will change the some configuration for our application.

54. Copy the RDS **Endpoint** value to the `notepad` for the later use. You can find it in **Database** section. It is located bottom of the **Configuration overview** page.

* <img src=./images/lab-ha-task5-rds-endpoint.png width=300>

55. In the **Software** section, click **Modify** button for the environment variable configuration.

56. In the **Modify software** page, you can find  **Environment properties** section. Configure following variables.

* **APP_HOST** : `0.0.0.0`
* **APP_PORT** : `5000`
* **DB_URL** : `mysql+pymysql://serverless:workshop@<YOUR DATABASE ENDPOINT>/ebdb?charset=utf8`
  * **NOTE**: Replace <YOUR DATABASE ENDPOINT> to **your own EndPoint** value which copied previous step. For example : `mysql+pymysql://serverless:workshop@aa1is6q2iidf84x.cjukz33spdko.ap-southeast-1.rds.amazonaws.com:3306/ebdb?charset=utf8`
* **EFS_ID** : `<EFD_ID>`
  * We already copied it to `notepad` in TASK 2.
  * For example : `fs-5d3e921c`
* **ELCACHE_EP** : `<ELCACHE_EP>`
  * We already copied it to `notepad` in TASK 3.
  * For example : `moving-to-serverless.ttvhbi.ng.0001.apse1.cache.amazonaws.com`
* **FLASK_SECRET** : `THIS_IS_THE_SECRET`
  * This value will be used for Flask app's SECRET_KEY.
* **GMAPS_KEY** : `<GMAPS_KEY>`
  * You already get this key from instructor.
* **UPLOAD_FOLDER** : `/mnt/efs`

 * <img src=./images/lab-ha-task5-eb-sw-env-var.png width=500>

57. Click **Apply** button.


58. In the **Load balancer** section, click **Modify** button.

59. In the **Modify load balancer** page, Find **Processes** section then click the checkbox of `default` process for the application health check configuration. And click the **Actions** button, then you can choose **Edit** menu.

 * <img src=./images/lab-ha-task5-eb-alb-health.png width=500>

60. Configure **Health check** variables.
 * **HTTP code** : `200`
 * **Path** : `/users/new`

 * <img src=./images/lab-ha-task5-eb-alb-health-2.png width=500>


61. Click **Save** button.

62. Next, click **Apply** button.

63. Click the **Dashboard** and click **Upload and Deploy** button.

64. You can download the application to your laptop as a ZIP file, from the below URL:
``
    https://s3.amazonaws.com/moving-to-serverless/prod/cloudalbum_v1.0.zip
``

65. Click the **Browse...** button and choose `cloudalbum_v1.0.zip` file which downloaded previous step. 

 * <img src=./images/lab-ha-task5-deploy.png width=500>

66. Click **Deploy** button.

67. After deploy operation, visit the our application URL. you can see our application in your browser like below.

 * <img src=./images/lab-ha-task5-cloudalbum.png width=500>


68. If the deployment is successful, Let's change our mimimum capacity configuration. In the **Capacity** section, click **Modify** button.


69. In the **Modify capacity** page, change the atttribute of AutoScalingGroup `Min` value from 1 to 2. (or what you want..)

 * <img src=./images/lab-ha-task5-asg.png width=500>


70. Click the **Apply** button. let's wait until the configuration is applied.

71. Test the deployed application and explore the ElasticBeastalk console.



## Challenge : Investigate the application changes

72. .ebextentions (설명 추가 예정)

73. SessionStore (설명 추가 예정)


## TASK 6. Remove your AWS resources.
(자원 삭제 상세설명 추가예정)

74. Remove your EB environment (RDS, ALB, ASG included). 

75. Remove your EFS.

76. Remove your Elasticache cluster.

77. Remove your Elasticache cluster.

78. Remove your VPC from CloudFormation console.


## Congratulations. You have successfully completed this hands-on lab.